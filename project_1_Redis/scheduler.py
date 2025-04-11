import time
from datetime import datetime
from db import SessionLocal, Meeting
from redis_client import r

def activate_meetings():
    session = SessionLocal()
    now = datetime.utcnow()
    
    # Find all meetings that should be active now
    meetings = session.query(Meeting).all()
    
    for meeting in meetings:
        if meeting.t1 <= now <= meeting.t2:
            # Check if already active
            if not r.sismember("active_meetings", meeting.meetingID):
                print(f"Activating meeting {meeting.meetingID}")

                r.sadd("active_meetings", meeting.meetingID)
                r.hset(f"meeting:{meeting.meetingID}", mapping={
                    "lat": str(meeting.lat),
                    "long": str(meeting.long),
                    "participants": meeting.participants
                })
        else:
            # Deactivate meeting if time is up
            if r.sismember("active_meetings", meeting.meetingID):
                print(f"Deactivating meeting {meeting.meetingID}")
                r.srem("active_meetings", meeting.meetingID)
                r.delete(f"meeting:{meeting.meetingID}")

    session.close()

# Optional: Run this in a loop (for testing)
if __name__ == "__main__":
    while True:
        activate_meetings()
        time.sleep(60)
