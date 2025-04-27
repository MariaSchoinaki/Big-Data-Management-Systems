from flask import Flask, request, jsonify, abort
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
import threading
import logging
from dateutil import tz
from src.redis_client import r
from src.db import Base, engine, init_db, SessionLocal, User, Meeting
from src.logic import *
from src.scheduler import run_scheduler_loop
from src.backend_utils import haversine, is_valid_email

app = Flask(__name__)

# ---Reset DB & Redis on startup (dev only)------
r.flushdb()
Base.metadata.drop_all(bind=engine)
init_db()

# ---Logging------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
@app.before_request
def log_request():
    logging.info(f"{request.method} {request.path} | args={request.args} | json={request.get_json(silent=True)}")

# ---Helpers------
def parse_int_id(raw, name="meetingID"):
    try:
        return int(raw)
    except (TypeError, ValueError):
        abort(400, description=f"'{name}' must be an integer, got {raw!r}")

# ---Health check------
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(status="ok"), 200

# Check if a user exists
@app.route("/user_exists/<email>", methods=["GET"])
def user_exists(email):
    sess = SessionLocal()
    exists = sess.get(User, email) is not None
    sess.close()
    return ("", 200) if exists else ("", 404)

# Check if a meeting exists
@app.route("/meeting_exists/<int:meetingID>", methods=["GET"])
def meeting_exists(meetingID):
    sess = SessionLocal()
    exists = sess.get(Meeting, meetingID) is not None
    sess.close()
    return ("", 200) if exists else ("", 404)

# ---User endpoints------
@app.route("/create_user", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    sess = SessionLocal()
    try:
        sess.add(User(**data))
        sess.commit()
        return jsonify(status="success", message=f"✅ User {data.get('email')} was created successfully!")
    except IntegrityError:
        sess.rollback()
        return jsonify(status="error", message="❌ Email already exists."), 400
    finally:
        sess.close()

@app.route("/delete_user", methods=["POST"])
def delete_user():
    email = request.json.get("email")
    sess = SessionLocal()
    user = sess.get(User, email)
    if not user:
        sess.close()
        return jsonify(status="error", message="❌ User not found."), 404
    sess.delete(user); sess.commit(); sess.close()
    return jsonify(status="success", message="✅ User deleted.")

# ---Meeting endpoints------
@app.route("/create_meeting", methods=["POST"])
def create_meeting():
    local = tz.gettz("Europe/Athens")  # or tz.tzlocal() if you prefer dynamic
    payload = request.get_json() or {}
    sess = SessionLocal()
    try:
        # 1) Parse the incoming participants string
        participants_csv = payload.get("participants", "")

        participants_raw = participants_csv if isinstance(participants_csv, list) else participants_csv.split(",")
    
        participants = []
        for email in participants_raw:
            if email and is_valid_email(email):
                participants.append(email.lower())
        
        participants = list(set(participants))  # deduplicate
        
        if not participants:
            return jsonify(status="error", message="❌ Please provide at least one valid participant email."), 400
        
        participants_str = ",".join(participants)

        # 2) Parse the incoming t1/t2 strings into real datetimes
        t1_str = payload.pop("t1")
        t2_str = payload.pop("t2")
        t1 = datetime.strptime(t1_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=local).astimezone(timezone.utc)
        t2 = datetime.strptime(t2_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=local).astimezone(timezone.utc)

        # 3) Build the Meeting (meetingID will auto‑increment)
        m = Meeting(
            title       = payload["title"].strip(),
            description = payload.get("description", ""),
            t1          = t1,
            t2          = t2,
            lat         = payload["lat"],
            long        = payload["long"],
            participants= participants_str

        )
        sess.add(m)
        sess.commit()

        return jsonify(
            status="success",
            meetingID=m.meetingID,
            message="Meeting created."
        ), 201

    except KeyError as ke:
        sess.rollback()
        return jsonify(status="error", message=f"Missing field: {ke}"), 400
    except ValueError as ve:
        sess.rollback()
        return jsonify(status="error", message=f"Invalid date format: {ve}"), 400
    finally:
        sess.close()

@app.route("/delete_meeting", methods=["POST"])
def delete_meeting():
    raw = request.json.get("meetingID")
    mid = parse_int_id(raw)
    sess = SessionLocal()
    m = sess.get(Meeting, mid)
    if not m:
        sess.close()
        return jsonify(status="error", message=f"❌ Meeting with ID {mid} not found."), 404
    sess.delete(m); sess.commit(); sess.close()
    return jsonify(status="success", message=f"✅ Meeting with ID {mid} deleted.")

@app.route("/get_nearby", methods=["GET"])
def api_get_nearby_active_meetings():
    email = request.args.get("email")
    lat = float(request.args.get("lat", 0))
    lon = float(request.args.get("long", 0))

    mids_with_dist = get_nearby_active_meetings(email, lat, lon)
    if mids_with_dist is None:
        return jsonify(error=f"❌ User {email} not found."), 404

    sess = SessionLocal()

    meetings = []
    for mid, distance in mids_with_dist:  # Unpack tuple
        meeting = sess.get(Meeting, int(mid))
        if meeting:
            meetings.append({
                "id": meeting.meetingID,
                "title": meeting.title,
                "t1": meeting.t1.strftime("%Y-%m-%d %H:%M:%S"),
                "t2": meeting.t2.strftime("%Y-%m-%d %H:%M:%S"),
                "distance_meters": round(distance, 2),
                "lat": meeting.lat,
                "long": meeting.long,
                "participants": meeting.participants or "None"
            })

    meetings = sorted(meetings, key=lambda x: x.get("distance_meters", float('inf')))

    sess.close()
    return jsonify(active_meetings=meetings)

@app.route("/active_meetings", methods=["GET"])
def api_get_active_meetings():
    sess = SessionLocal()
    meetings = []
    for mid in get_active_meetings():
        meeting = sess.get(Meeting, int(mid))
        if meeting:
            meetings.append({
                "id": meeting.meetingID,
                "title": meeting.title,
                "t1": meeting.t1.strftime("%Y-%m-%d %H:%M:%S") if meeting.t1 else None,
                "t2": meeting.t2.strftime("%Y-%m-%d %H:%M:%S") if meeting.t2 else None,
                "lat": meeting.lat,
                "long": meeting.long,
                "participants": meeting.participants or "None" 
            })
    # Sort by start time
    meetings = sorted(meetings, key=lambda x: x["t1"])
    sess.close()
    return jsonify(active_meetings=meetings)

@app.route("/join", methods=["POST"])
def api_join():
    data = request.get_json() or {}
    mid   = parse_int_id(data.get("meetingID"))
    email = data.get("email")
    return jsonify(join_meeting(email, mid))

@app.route("/leave", methods=["POST"])
def api_leave():
    data = request.get_json() or {}
    mid   = parse_int_id(data.get("meetingID"))
    email = data.get("email")
    return jsonify(leave_meeting(email, mid))

@app.route("/end_meeting", methods=["POST"])
def api_end_meeting():
    raw = request.json.get("meetingID")
    mid = parse_int_id(raw)
    return jsonify(end_meeting(mid))

@app.route("/post_message", methods=["POST"])
def api_post_message():
    data = request.get_json() or {}
    mid = parse_int_id(data.get("meetingID"))
    result = post_message(data.get("email"), data.get("message"), mid)

    if result["status"] == "error":
        return jsonify(result), 400  # Send 400 if error
    else:
        return jsonify(result), 200

@app.route("/get_chat", methods=["GET"])
def api_get_chat():
    raw = request.args.get("meetingID")
    mid = parse_int_id(raw)
    return jsonify(meetingID=mid, messages=get_chat(mid))

@app.route("/user_messages", methods=["GET"])
def api_user_messages():
    email = request.args.get("email")
    sess = SessionLocal()

    user = sess.get(User, email)
    if user is None:
        sess.close()
        return jsonify(error=f"❌ User {email} not found."), 404

    # If user exists
    messages = get_user_messages(email)
    sess.close()
    return jsonify(email=email, messages=messages)

@app.route("/user_chat_in_meeting", methods=["GET"])
def api_user_chat_in_meeting():
    email = request.args.get("email")
    result = show_user_chat_in_meeting(email)
    
    if result.get("status") == "error":
        return jsonify(result), 400  # Send 400 if user not in any meeting
    else:
        return jsonify(result), 200

@app.route("/get_all_users", methods=["GET"])
def api_get_all_users():
    sess = SessionLocal()
    users = sess.query(User).all()
    sess.close()
    return jsonify(emails=[u.email for u in users])

from src.scheduler import run_scheduler_loop_once
@app.route("/force_scheduler", methods=["POST"])
def api_run_scheduler_once():
    run_scheduler_loop_once()
    return jsonify(status="ok", message="❕Scheduler ran once.")

# ---Entrypoint------
if __name__ == "__main__":
    # Start scheduler in a background thread
    threading.Thread(target=run_scheduler_loop, daemon=True).start()

    # Launch Flask
    app.run(host="0.0.0.0", port=5000, debug=True)