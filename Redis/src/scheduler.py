import time
from datetime import datetime, timezone
from src.db import SessionLocal, Meeting
from src.redis_client import r

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def run_scheduler_loop():
    logging.info("[Scheduler] Background scheduler started.")
    
    try:
        r.ping()
        logging.info("✅ Redis connection is active.")
    except Exception as e:
        logging.error(f"❌ Redis connection failed: {e}")
        return  # Exit early if Redis isn't reachable

    while True:
        sess = SessionLocal()
        now = datetime.now(timezone.utc)
        updated_meetings = 0

        for m in sess.query(Meeting).all():
            logging.info(f"Checking meeting {m.meetingID} → t1={m.t1}, t2={m.t2}, now={now}")
            
            t1 = m.t1 if m.t1.tzinfo else m.t1.replace(tzinfo=timezone.utc)
            t2 = m.t2 if m.t2.tzinfo else m.t2.replace(tzinfo=timezone.utc)

            if t1 <= now <= t2:
                if not r.sismember("active_meetings", m.meetingID):
                    r.sadd("active_meetings", m.meetingID)
                    r.hset(f"meeting:{m.meetingID}", mapping={
                        "lat": str(m.lat),
                        "long": str(m.long),
                        "participants": m.participants
                    })
                    logging.info(f"📌 Meeting {m.meetingID} marked as active in Redis.")
                    updated_meetings += 1
            else:
                if r.sismember("active_meetings", m.meetingID):
                    r.srem("active_meetings", m.meetingID)
                    r.delete(f"meeting:{m.meetingID}")
                    logging.info(f"❌ Meeting {m.meetingID} removed from Redis (expired).")

        sess.close()
        logging.info(f"Scheduler ran, updated {updated_meetings} meetings.")
        time.sleep(60) # 60
       
# For testing and/or use just when a meeting is created
def run_scheduler_loop_once():
    logging.info("[Scheduler] Running single pass (on-demand).")
    try:
        r.ping()
        logging.info("✅ Redis connection is active.")
    except Exception as e:
        logging.error(f"❌ Redis connection failed: {e}")
        return

    sess = SessionLocal()
    now = datetime.now(timezone.utc)
    updated_meetings = 0

    for m in sess.query(Meeting).all():
        logging.info(f"Checking meeting {m.meetingID} → t1={m.t1}, t2={m.t2}, now={now}")
        
        t1 = m.t1 if m.t1.tzinfo else m.t1.replace(tzinfo=timezone.utc)
        t2 = m.t2 if m.t2.tzinfo else m.t2.replace(tzinfo=timezone.utc)

        if t1 <= now <= t2:
            if not r.sismember("active_meetings", m.meetingID):
                r.sadd("active_meetings", m.meetingID)
                r.hset(f"meeting:{m.meetingID}", mapping={
                    "lat": str(m.lat),
                    "long": str(m.long),
                    "participants": m.participants
                })
                logging.info(f"📌 Meeting {m.meetingID} marked as active in Redis.")
                updated_meetings += 1
        else:
            if r.sismember("active_meetings", m.meetingID):
                r.srem("active_meetings", m.meetingID)
                r.delete(f"meeting:{m.meetingID}")
                logging.info(f"❌ Meeting {m.meetingID} removed from Redis (expired).")

    sess.close()
    logging.info(f"Scheduler single pass completed, updated {updated_meetings} meetings.")