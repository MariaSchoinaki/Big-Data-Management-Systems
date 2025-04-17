from src.redis_client import r
from src.utils import haversine
from src.db import SessionLocal, Log, Meeting
from datetime import datetime
import json

def get_nearby_active_meetings(email, x, y):
    session = SessionLocal()
    active_keys = r.smembers("active_meetings")  # Use a Redis set to track active meetings
    nearby = []
    print(f"{email} is at ({x}, {y}).")
    for meeting_id in active_keys:
        # Load meeting metadata from Redis (lat, long, participants)
        m_key = f"meeting:{meeting_id}"
        m_data = r.hgetall(m_key)

        if not m_data:
            continue

        lat = float(m_data.get("lat"))
        lon = float(m_data.get("long"))
        participants = m_data.get("participants", "").split(',')

        if email not in participants:
            continue

        distance = haversine(float(x), float(y), lat, lon)
        print(f"Meeting {meeting_id} is {distance} km away")
        if distance <= 100:
            nearby.append(meeting_id)

    session.close()
    return nearby

def join_meeting(email, meetingID):
    session = SessionLocal()
    joined_key = f"joined:{meetingID}"

    # Check if already joined this meeting
    if r.sismember(joined_key, email):
        session.close()
        return {
            "status": "error",
            "message": f"User {email} has already joined meeting {meetingID}."
        }

    # Check if user is already in any other active meeting (Physical Meetings imply that `A user can only be in one meeting at a time.`)
    active_meetings = r.smembers("active_meetings")
    for mid in active_meetings:
        if r.sismember(f"joined:{mid}", email):
            session.close()
            return {
                "status": "error",
                "message": f"User {email} is already in meeting {mid} and must leave it first."
            }

    # Add to Redis
    r.sadd(joined_key, email)

    # Log join
    log_entry = Log(
        email=email,
        meetingID=meetingID,
        action=1,
        timestamp=datetime.utcnow()
    )
    session.add(log_entry)
    session.commit()
    session.close()

    return {
        "status": "success",
        "message": f"User {email} joined meeting {meetingID}."
    }

def leave_meeting(email, meetingID):
    session = SessionLocal()
    joined_key = f"joined:{meetingID}"

    # Check if user has joined
    if not r.sismember(joined_key, email):
        session.close()
        return {
            "status": "error",
            "message": f"User {email} has not joined meeting {meetingID}."
        }

    # Remove from Redis
    r.srem(joined_key, email)

    # Log action
    log_entry = Log(
        email=email,
        meetingID=meetingID,
        action=2,  # leave_meeting
        timestamp=datetime.utcnow()
    )
    session.add(log_entry)
    session.commit()
    session.close()

    return {
        "status": "success",
        "message": f"User {email} left meeting {meetingID}."
    }
    
def get_joined_participants(meetingID):
    joined_key = f"joined:{meetingID}"
    participants = r.smembers(joined_key)

    return {
        "meetingID": meetingID,
        "participants": list(participants)
    }
    
def get_active_meetings():
    active = r.smembers("active_meetings")
    return {
        "active_meetings": list(active)
    }

def end_meeting(meetingID):
    session = SessionLocal()
    
    # Get participants
    joined_key = f"joined:{meetingID}"
    participants = r.smembers(joined_key)

    # Log time_out (action = 3)
    for email in participants:
        log_entry = Log(
            email=email,
            meetingID=meetingID,
            action=3,
            timestamp=datetime.utcnow()
        )
        session.add(log_entry)

    # Clean up Redis
    r.srem("active_meetings", meetingID)
    r.delete(f"meeting:{meetingID}")
    r.delete(joined_key)
    r.delete(f"chat:{meetingID}")  # if chat exists

    session.commit()
    session.close()

    return {
        "status": "success",
        "message": f"Meeting {meetingID} ended. {len(participants)} participants timed out."
    }
    
def post_message(email, message):
    # Find which meeting the user is in
    meeting_id = None
    active_meetings = r.smembers("active_meetings")

    for m_id in active_meetings:
        if r.sismember(f"joined:{m_id}", email):
            meeting_id = m_id
            break

    if not meeting_id:
        return {
            "status": "error",
            "message": f"User {email} is not in any active meeting."
        }

    msg_obj = {
        "email": email,
        "timestamp": datetime.utcnow().isoformat(),
        "message": message
    }

    r.rpush(f"chat:{meeting_id}", json.dumps(msg_obj))

    return {
        "status": "success",
        "message": f"Message posted to chat for meeting {meeting_id}."
    }
    
def get_chat(meetingID):
    chat_key = f"chat:{meetingID}"
    raw_msgs = r.lrange(chat_key, 0, -1)

    messages = [json.loads(m) for m in raw_msgs]
    return {
        "meetingID": meetingID,
        "messages": messages
    }

def get_user_messages(email):
    active_meetings = r.smembers("active_meetings")
    results = []

    for m_id in active_meetings:
        chat_key = f"chat:{m_id}"
        raw_msgs = r.lrange(chat_key, 0, -1)
        for raw in raw_msgs:
            msg = json.loads(raw)
            if msg["email"] == email:
                results.append({ "meetingID": m_id, **msg })

    return {
        "email": email,
        "messages": results
    }

def show_user_chat_in_meeting(email):
    # Find which meeting the user is in
    active_meetings = r.smembers("active_meetings")
    meeting_id = None

    for m_id in active_meetings:
        if r.sismember(f"joined:{m_id}", email):
            meeting_id = m_id
            break

    if not meeting_id:
        return {
            "status": "error",
            "message": f"User {email} is not in any active meeting."
        }

    # Get chat messages
    chat_key = f"chat:{meeting_id}"
    raw_msgs = r.lrange(chat_key, 0, -1)
    user_msgs = [
        json.loads(m) for m in raw_msgs
        if json.loads(m)["email"] == email
    ]

    return {
        "meetingID": meeting_id,
        "email": email,
        "messages": user_msgs
    }