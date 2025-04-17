import time
from datetime import datetime
from src.db import SessionLocal, Meeting
from src.redis_client import r

def activate_meetings():
    session = SessionLocal()
    now = datetime.utcnow()
    
    # Find all meetings that should be active now
    meetings = session.query(Meeting).all()
    
    for meeting in meetings:
        if meeting.t1 <= now <= meeting.t2:
            # Check if already active
            if not r.sismember("active_meetings", meeting.meetingID):
                print(f"\nActivating meeting {meeting.meetingID}")

                r.sadd("active_meetings", meeting.meetingID)
                r.hset(f"meeting:{meeting.meetingID}", mapping={
                    "lat": str(meeting.lat),
                    "long": str(meeting.long),
                    "participants": meeting.participants
                })
        else:
            # Deactivate meeting if time is up
            if r.sismember("active_meetings", meeting.meetingID):
                print(f"\nDeactivating meeting {meeting.meetingID}")
                r.srem("active_meetings", meeting.meetingID)
                r.delete(f"meeting:{meeting.meetingID}")

    session.close()

# Used to create a thread to activate meetings (check every 1m in the background)
def run_scheduler_loop():
    while True:
        activate_meetings()
        time.sleep(60)