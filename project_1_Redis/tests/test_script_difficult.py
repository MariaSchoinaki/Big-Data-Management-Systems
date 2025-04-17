import os, sys

# insert the project root (one level up) onto sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db import Base, engine, init_db, SessionLocal, User, Meeting
from src.logic import *
from src.scheduler import activate_meetings, run_scheduler_loop
from datetime import datetime, timezone, timedelta
import time
import threading

"""
Advanced Test Scenario:

This script resets the database and simulates a multi-user, multi-meeting workflow using the Redis-backed meeting system.

Three users are created: Alice, Bob, and Carol. 
Four meetings are created:
1. "team-sync" with Alice and Bob (active)
2. "dev-huddle" with Bob and Carol (active)
3. "ops-checkin" (active and near Bob)
4. "product-briefing" (future/NOT active, but also near Bob)

The scheduler is triggered to register the active meetings into Redis.
Users join their respective meetings. Bob later leaves "team-sync" and joins "dev-huddle" to simulate switching physical meetings.
Nearby meeting detection is tested for Bob based on his location coordinates.
Each user posts chat messages to the meeting they've joined. Full chat logs for both meetings are retrieved, as well as user-specific message logs.
Finally, Carol's messages in "dev-huddle" are isolated, and the "team-sync" meeting is ended. This tests the timeout logging and Redis cleanup.
This scenario validates full integration between the SQL database, Redis, scheduler logic, and chat system in a realistic use case.
"""

# --- Reset DB and Redis ---
r.flushdb()
Base.metadata.drop_all(bind=engine)
init_db()
session = SessionLocal()

# --- Users ---
users = [
    User(email="alice@example.com", name="Alice", age=30, gender="F"),
    User(email="bob@example.com", name="Bob", age=32, gender="M"),
    User(email="carol@example.com", name="Carol", age=28, gender="F")
]
for user in users:
    session.add(user)

# --- Meetings ---
now = datetime.now(timezone.utc)
meetings = [
    Meeting(
        meetingID="team-sync",
        title="Team Sync",
        description="Daily standup",
        t1=now - timedelta(minutes=5),
        t2=now + timedelta(minutes=25),
        lat=37.976,
        long=23.733,
        participants="alice@example.com,bob@example.com"
    ),
    Meeting(
        meetingID="dev-huddle",
        title="Dev Huddle",
        description="Sprint planning",
        t1=now - timedelta(minutes=2),
        t2=now + timedelta(minutes=15),
        lat=37.976,
        long=23.733,
        participants="bob@example.com,carol@example.com"
    ),
    Meeting(
        meetingID="ops-checkin",
        title="Ops Check-in",
        description="Site reliability roundtable",
        t1=now - timedelta(minutes=1),
        t2=now + timedelta(minutes=20),
        lat=37.9761,
        long=23.7331,
        participants="bob@example.com"
    ),
    Meeting(
        meetingID="product-briefing",
        title="Product Briefing",
        description="Upcoming launch preview",
        t1=now + timedelta(minutes=15),  # not yet active
        t2=now + timedelta(minutes=45),
        lat=37.9762,
        long=23.7332,
        participants="bob@example.com"
    )
]
for m in meetings:
    session.add(m)
session.commit()

# --- Activate meetings in background ---

threading.Thread(target=run_scheduler_loop, daemon=True).start()

# --- Join meetings ---
print(join_meeting("alice@example.com", "team-sync"))
print(join_meeting("bob@example.com", "team-sync"))
print(join_meeting("carol@example.com", "dev-huddle"))

# --- Bob switches meetings ---
print("\nBob leaving team-sync and joining dev-huddle")
print(leave_meeting("bob@example.com", "team-sync"))
print(join_meeting("bob@example.com", "dev-huddle"))

# --- Nearby meetings for Bob ---
print("\nNearby active meetings for Bob:")
print(get_nearby_active_meetings("bob@example.com", 37.976, 23.733))

# --- Post messages ---
print(post_message("bob@example.com", "We're starting now!"))
print(post_message("bob@example.com", "Can someone pull up the doc?"))
print(post_message("bob@example.com", "Just posted the link above."))
print(post_message("carol@example.com", "I'll join in 2 minutes."))
print(post_message("carol@example.com", "Just finishing another call."))
print(post_message("carol@example.com", "I'm here now."))
print(post_message("alice@example.com", "Morning team!"))

# --- Fetch chats ---
print("\nChat in team-sync:")
print(get_chat("team-sync"))

print("\nChat in dev-huddle:")
print(get_chat("dev-huddle"))

# --- User messages ---
print("\nMessages posted by Bob:")
print(get_user_messages("bob@example.com"))

# --- User chat in meeting ---
print("\nCarol's messages in dev-huddle:")
print(show_user_chat_in_meeting("carol@example.com"))

# --- End a meeting ---
print("\nEnding meeting 'team-sync':")
print(end_meeting("team-sync"))

session.close()