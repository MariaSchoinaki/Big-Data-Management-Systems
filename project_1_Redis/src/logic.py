import json
from dateutil import parser
from datetime import datetime, timezone

from src.redis_client import r
from src.db import SessionLocal, Log, Meeting, User
from src.backend_utils import haversine, decode_redis_set

def get_nearby_active_meetings(email, x, y):
    sess = SessionLocal()
    user = sess.get(User, email)
    if user is None:
        sess.close()
        return None

    out = []
    for mid in decode_redis_set(r.smembers("active_meetings")):
        m = r.hgetall(f"meeting:{mid}")
        if not m:
            continue
        if email not in [e.strip() for e in m.get("participants", "").split(',')]:
            continue
        dist = haversine(x, y, float(m['lat']), float(m['long']))
        if dist <= 100:
            out.append((mid, dist))  # <-- List of tuples: (meeting ID, distance)
    sess.close()
    return out

def join_meeting(email, meetingID):
    sess = SessionLocal()

    user = sess.get(User, email)
    if user is None:
        sess.close()
        return {"status": "error", "message": f"❌ User {email} does not exist."}

    meeting = sess.get(Meeting, meetingID)
    if meeting is None:
        sess.close()
        return {"status": "error", "message": f"❌ Meeting with ID {meetingID} not found."}

    if not r.sismember("active_meetings", meetingID):
        sess.close()
        return {"status": "error", "message": f"❌ Meeting with ID {meetingID} is not active."}

    invited = [e.strip() for e in meeting.participants.split(',')]
    if email not in invited:
        sess.close()
        return {"status": "error", "message": "❌ You are not invited to this meeting."}

    for mid in r.smembers("active_meetings"):
        if r.sismember(f"joined:{mid}", email):
            sess.close()
            return {"status": "error", "message": f"❌ User {email} has already joined meeting {mid}", "status_code": 409}

    r.sadd(f"joined:{meetingID}", email)

    sess.add(Log(email=email, meetingID=meetingID, action=1, timestamp=datetime.now(timezone.utc)))
    sess.commit()
    sess.close()
    return {"status": "success", "message": f"✅ User {email} has joined meeting {meetingID}."}


def leave_meeting(email, meetingID):
    sess=SessionLocal()
    if not r.sismember(f"joined:{meetingID}", email):
        sess.close(); return {"status":"error","message":f"❌ {email} has not joined the meeting"}
    r.srem(f"joined:{meetingID}", email)
    sess.add(Log(email=email, meetingID=meetingID, action=2, timestamp=datetime.now(timezone.utc)))
    sess.commit(); sess.close()
    return {"status":"success","message":f"✅ {email} has left the meeting with ID {meetingID}."}

def get_active_meetings():
    return [mid for mid in decode_redis_set(r.smembers("active_meetings"))]

def end_meeting(meetingID):
    sess=SessionLocal(); members=r.smembers(f"joined:{meetingID}")
    for e in members: sess.add(Log(email=e, meetingID=meetingID, action=3, timestamp=datetime.now(timezone.utc)))
    sess.commit(); sess.close()
    r.srem("active_meetings", meetingID)
    r.delete(f"meeting:{meetingID}", f"joined:{meetingID}", f"chat:{meetingID}")
    return {"status":"success","message":f"✅ Meeting with ID {meetingID} has ended. | {len(members)} participants timed out"}

def post_message(email, message, meetingID):
    sess = SessionLocal()

    user = sess.get(User, email)
    if user is None:
        sess.close()
        return {"status": "error", "message": f"❌ User {email} does not exist."}

    if not r.sismember(f"joined:{meetingID}", email):
        sess.close()
        return {"status": "error", "message": "❌ You must join the meeting first."}

    # Save chat message into Redis
    payload = {"email": email, "message": message, "timestamp": datetime.now(timezone.utc).isoformat()}
    r.rpush(f"chat:{meetingID}", json.dumps(payload))

    sess.close()
    return {"status": "success", "message": "✅ Message posted."}

def get_chat(meetingID):
    return [json.loads(m) for m in r.lrange(f"chat:{meetingID}",0,-1)]

def get_user_messages(email):
    sess = SessionLocal()
    out = []
    for mid in r.smembers("active_meetings"):
        mid = int(mid)
        meeting = sess.get(Meeting, mid)
        if not meeting:
            continue
        for raw in r.lrange(f"chat:{mid}", 0, -1):
            m = json.loads(raw)
            if m["email"] == email:
                out.append({
                    "message": m["message"],
                    "timestamp": m["timestamp"],
                    "meetingID": meeting.meetingID,
                    "title": meeting.title
                })
    sess.close()
     # Sort by timestamp ascending (earliest first)
    out = sorted(out, key=lambda m: parser.isoparse(m["timestamp"]))
    return out

def show_user_chat_in_meeting(email):
    for mid in r.smembers("active_meetings"):
        if r.sismember(f"joined:{mid}", email):
            return {"meetingID":int(mid), "msgs":get_chat(mid)}
    return {"status":"error","message":"❌ Not in any meeting"}