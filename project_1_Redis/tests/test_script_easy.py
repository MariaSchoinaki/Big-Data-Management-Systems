"""
Basic Single User Test Script for Redis Meeting App

This script tests:
- Creating a user
- Creating an active meeting
- Scheduler activating the meeting into Redis
- User joining the meeting
- Checking nearby meetings
- Posting and retrieving chat messages
- Ending the meeting (and cleaning up)
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

# --- Setup ---
session = SessionLocal()

# Create test user
user = User(email="test@example.com", name="TestUser", age=25, gender="M")
session.add(user)

# Create a meeting that is currently active
meeting = Meeting(
    title="Test Meeting",
    description="Test Description",
    t1=datetime.now(timezone.utc) - timedelta(minutes=5),
    t2=datetime.now(timezone.utc) + timedelta(minutes=30),
    lat=37.9838,
    long=23.7275,
    participants="test@example.com"
)
session.add(meeting)
session.commit()

session.close()

# --- Activate Meetings ---
run_scheduler_loop_once()

# --- Actions ---
print("\n✅ Trying to join the meeting...")
print(join_meeting("test@example.com", 1))

print("\n✅ Checking nearby active meetings...")
print(get_nearby_active_meetings("test@example.com", 37.9838, 23.7275))

print("\n✅ Posting a chat message...")
print(post_message("test@example.com", "Hello from test_script_easy!", 1))

print("\n✅ Retrieving full chat...")
print(get_chat(1))

print("\n✅ Retrieving all user messages...")
print(get_user_messages("test@example.com"))

print("\n✅ Showing user chat in joined meeting...")
print(show_user_chat_in_meeting("test@example.com"))

print("\n✅ Ending the meeting...")
print(end_meeting(1))

stop_redis_container()