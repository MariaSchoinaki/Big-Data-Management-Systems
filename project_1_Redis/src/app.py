from flask import Flask, request, jsonify
from src.db import Base, engine, init_db, SessionLocal, User, Meeting
from src.logic import *
from src.scheduler import run_scheduler_loop
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import threading
import logging

app = Flask(__name__)
# --- Reset DB and Redis ---
r.flushdb()
Base.metadata.drop_all(bind=engine)
init_db()
session = SessionLocal()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

@app.route("/health")
def health_check():
    return {"status": "ok"}, 200

@app.before_request
def log_request_info():
    logging.info(f"{request.method} {request.path} | args: {request.args} | json: {request.get_json(silent=True)}")

@app.route("/create_user", methods=["POST"])
def create_user():
    session = SessionLocal()
    try:
        data = request.get_json()
        user = User(**data)
        session.add(user)
        session.commit()
        return jsonify({"status": "success", "message": "User created."})
    except IntegrityError:
        session.rollback()
        return jsonify({"status": "error", "message": "User with this email already exists."}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

@app.route("/delete_user", methods=["POST"])
def delete_user():
    session = SessionLocal()
    try:
        email = request.json["email"]
        user = session.query(User).get(email)
        if user:
            session.delete(user)
            session.commit()
            return jsonify({"status": "success", "message": "User deleted"})
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404
    except Exception as e:
        session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

from datetime import datetime

@app.route("/create_meeting", methods=["POST"])
def create_meeting():
    payload = request.get_json()
    session = SessionLocal()
    try:
        # parse the incoming t1/t2 strings into real datetimes
        # adjust the format to match exactly what your GUI is sending
        t1_str = payload.pop("t1")
        t2_str = payload.pop("t2")
        t1 = datetime.strptime(t1_str, "%Y-%m-%d %H:%M:%S")
        t2 = datetime.strptime(t2_str, "%Y-%m-%d %H:%M:%S")

        # now build the Meeting with real datetimes
        meeting = Meeting(
            meetingID   = payload["meetingID"],
            title       = payload["title"],
            description = payload["description"],
            t1          = t1,
            t2          = t2,
            lat         = payload["lat"],
            long        = payload["long"],
            participants= payload["participants"],
        )

        session.add(meeting)
        session.commit()
        return jsonify(status="success", message="Meeting created.")
    except ValueError as ve:
        session.rollback()
        return jsonify(status="error", message=f"Invalid date format: {ve}"), 400
    except IntegrityError:
        session.rollback()
        return jsonify(status="error", message="Meeting ID already exists."), 400
    finally:
        session.close()


@app.route("/delete_meeting", methods=["POST"])
def delete_meeting():
    session = SessionLocal()
    try:
        meetingID = request.json["meetingID"]
        meeting = session.query(Meeting).get(meetingID)
        if meeting:
            session.delete(meeting)
            session.commit()
            return jsonify({"status": "success", "message": "Meeting deleted"})
        else:
            return jsonify({"status": "error", "message": "Meeting not found"}), 404
    except Exception as e:
        session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

@app.route("/get_nearby", methods=["GET"])
def get_nearby():
    try:
        email = request.args["email"]
        x = float(request.args["lat"])
        y = float(request.args["long"])
        return jsonify(get_nearby_active_meetings(email, x, y))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/join", methods=["POST"])
def join():
    data = request.get_json()
    return jsonify(join_meeting(data["email"], data["meetingID"]))

@app.route("/leave", methods=["POST"])
def leave():
    data = request.get_json()
    return jsonify(leave_meeting(data["email"], data["meetingID"]))

@app.route("/active_meetings", methods=["GET"])
def active():
    return jsonify(get_active_meetings())

@app.route("/end_meeting", methods=["POST"])
def end():
    return jsonify(end_meeting(request.json["meetingID"]))

@app.route("/post_message", methods=["POST"])
def post():
    data = request.get_json()
    return jsonify(post_message(data["email"], data["message"]))

@app.route("/get_chat", methods=["GET"])
def chat():
    return jsonify(get_chat(request.args["meetingID"]))

@app.route("/user_messages", methods=["GET"])
def user_messages():
    return jsonify(get_user_messages(request.args["email"]))

@app.route("/user_chat_in_meeting", methods=["GET"])
def user_chat():
    return jsonify(show_user_chat_in_meeting(request.args["email"]))

if __name__ == "__main__":
    threading.Thread(target=run_scheduler_loop, daemon=True).start()
    app.run(debug=True, host="0.0.0.0")