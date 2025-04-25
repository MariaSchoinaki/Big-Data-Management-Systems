import json
from datetime import datetime
from src.redis_client import r
from src.db import SessionLocal, Log, Meeting, User
from src.utils import haversine

def get_nearby_active_meetings(email, x, y):
    sess = SessionLocal()
    if sess.get(User, email) is None:
        sess.close(); return []
    out = []
    for mid in r.smembers("active_meetings"):
        m = r.hgetall(f"meeting:{mid}")
        if not m: continue
        if email not in [e.strip() for e in m.get("participants","").split(',')]:
            continue
        dist = haversine(x, y, float(m['lat']), float(m['long']))
        if dist <= 100: out.append(int(mid))
    sess.close()
    return out

def join_meeting(email, meetingID):
    sess = SessionLocal()
    if sess.get(User, email) is None:
        sess.close(); return {"status":"error","message":"User not found"}
    if sess.get(Meeting, meetingID) is None:
        sess.close(); return {"status":"error","message":"Meeting not found"}
    if not r.sismember("active_meetings", meetingID):
        sess.close(); return {"status":"error","message":"Not active"}
    # invite check
    invited = sess.get(Meeting, meetingID).participants.split(',')
    if email not in invited:
        sess.close(); return {"status":"error","message":"Not invited"}
    # one meeting at a time
    for mid in r.smembers("active_meetings"):
        if r.sismember(f"joined:{mid}", email):
            sess.close(); return {"status":"error","message":f"Already in {mid}"}
    r.sadd(f"joined:{meetingID}", email)
    sess.add(Log(email=email, meetingID=meetingID, action=1, timestamp=datetime.utcnow()))
    sess.commit(); sess.close()
    return {"status":"success","message":"Joined"}

def leave_meeting(email, meetingID):
    sess=SessionLocal()
    if not r.sismember(f"joined:{meetingID}", email):
        sess.close(); return {"status":"error","message":"Not joined"}
    r.srem(f"joined:{meetingID}", email)
    sess.add(Log(email=email, meetingID=meetingID, action=2, timestamp=datetime.utcnow()))
    sess.commit(); sess.close()
    return {"status":"success","message":"Left"}

def get_active_meetings(): return [int(m) for m in r.smembers("active_meetings")]

def end_meeting(meetingID):
    sess=SessionLocal(); members=r.smembers(f"joined:{meetingID}")
    for e in members: sess.add(Log(email=e, meetingID=meetingID, action=3, timestamp=datetime.utcnow()))
    sess.commit(); sess.close()
    r.srem("active_meetings", meetingID)
    r.delete(f"meeting:{meetingID}", f"joined:{meetingID}", f"chat:{meetingID}")
    return {"status":"success","timed_out":len(members)}

def post_message(email, message, meetingID):
    if not r.sismember(f"joined:{meetingID}", email):
        return {"status":"error","message":"Not in meeting"}
    msg={"email":email,"timestamp":datetime.utcnow().isoformat(),"message":message}
    r.rpush(f"chat:{meetingID}", json.dumps(msg))
    return {"status":"success"}

def get_chat(meetingID):
    return [json.loads(m) for m in r.lrange(f"chat:{meetingID}",0,-1)]

def get_user_messages(email):
    out=[]
    for mid in r.smembers("active_meetings"):
        for raw in r.lrange(f"chat:{mid}",0,-1):
            m=json.loads(raw)
            if m["email"]==email: out.append(m)
    return out

def show_user_chat_in_meeting(email):
    for mid in r.smembers("active_meetings"):
        if r.sismember(f"joined:{mid}", email):
            return {"meetingID":int(mid), "msgs":get_chat(mid)}
    return {"status":"error","message":"Not in any"}