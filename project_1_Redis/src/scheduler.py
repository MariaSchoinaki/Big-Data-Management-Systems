import time
from datetime import datetime
from src.db import SessionLocal, Meeting
from src.redis_client import r

def run_scheduler_loop():
    while True:
        sess = SessionLocal()
        now = datetime.utcnow()
        for m in sess.query(Meeting).all():
            if m.t1 <= now <= m.t2:
                if not r.sismember("active_meetings", m.meetingID):
                    r.sadd("active_meetings", m.meetingID)
                    r.hset(f"meeting:{m.meetingID}", mapping={
                        "lat":str(m.lat), "long":str(m.long), "participants":m.participants
                    })
            else:
                if r.sismember("active_meetings", m.meetingID):
                    r.srem("active_meetings", m.meetingID)
                    r.delete(f"meeting:{m.meetingID}")
        sess.close()
        time.sleep(60)