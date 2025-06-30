"""
Advanced Multi-User, Multi-Meeting Test Script for Redis Meeting App

Simulates:
- 3 users: Alice, Bob, Carol
- 4 meetings (3 active, 1 future)
- Multiple joins, leaves, nearby detection, chat posting
- Final meeting ending and Redis cleanup
"""

from test_utils import *
ensure_redis_running()

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db import Base, engine, init_db, SessionLocal, User, Meeting
from src.logic import *
from src.scheduler import run_scheduler_loop_once
from datetime import datetime, timezone, timedelta

# --- Reset Environment ---
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
session.add_all(users)

# --- Meetings ---
now = datetime.now(timezone.utc)
meetings = [
    Meeting(
        title="Team Sync",
        description="Daily standup meeting",
        t1=now - timedelta(minutes=10),
        t2=now + timedelta(minutes=20),
        lat=37.976,
        long=23.733,
        participants="alice@example.com,bob@example.com"
    ),
    Meeting(
        title="Dev Huddle",
        description="Sprint planning session",
        t1=now - timedelta(minutes=5),
        t2=now + timedelta(minutes=25),
        lat=37.976,
        long=23.733,
        participants="bob@example.com,carol@example.com"
    ),
    Meeting(
        title="Ops Check-in",
        description="Infrastructure discussion",
        t1=now - timedelta(minutes=3),
        t2=now + timedelta(minutes=15),
        lat=37.9761,
        long=23.7331,
        participants="bob@example.com"
    ),
    Meeting(
        title="Product Briefing",
        description="Future product presentation",
        t1=now + timedelta(minutes=30),  # not yet active
        t2=now + timedelta(minutes=60),
        lat=37.9762,
        long=23.7332,
        participants="bob@example.com"
    )
]
session.add_all(meetings)
session.commit()

session.close()

# --- Activate Meetings ---
run_scheduler_loop_once()

# --- Actions ---
print("\n✅ Users joining their meetings...")
print(join_meeting("alice@example.com", 1))
print(join_meeting("bob@example.com", 1))
print(join_meeting("carol@example.com", 2))

# Bob switches meetings
print("\n✅ Bob leaving 'Team Sync' and joining 'Dev Huddle'...")
print(leave_meeting("bob@example.com", 1))
print(join_meeting("bob@example.com", 2))

# Nearby Meetings
print("\n✅ Nearby meetings for Bob:")
print(get_nearby_active_meetings("bob@example.com", 37.976, 23.733))

# Post chat messages
print("\n✅ Posting messages...")
print(post_message("alice@example.com", "Morning all!", 1))
print(post_message("bob@example.com", "Hello, starting now!", 2))
print(post_message("carol@example.com", "Joining in a few minutes!", 2))

# Retrieve chats
print("\n✅ Chat in 'Team Sync':")
print(get_chat(1))

print("\n✅ Chat in 'Dev Huddle':")
print(get_chat(2))

# User Messages
print("\n✅ Messages posted by Bob:")
print(get_user_messages("bob@example.com"))

# Show Carol's chat
print("\n✅ Carol's chat in 'Dev Huddle':")
print(show_user_chat_in_meeting("carol@example.com"))

# End meeting
print("\n✅ Ending 'Team Sync' meeting:")
print(end_meeting(1))

stop_redis_container()