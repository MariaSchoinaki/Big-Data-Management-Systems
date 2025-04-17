import os, sys

# insert the project root (one level up) onto sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db import Base, engine, init_db, SessionLocal, User, Meeting
from src.logic import *
from src.scheduler import activate_meetings
from datetime import datetime, timezone, timedelta


"""
Basic Test Scenario:

This script performs a single-user test case to verify core functionality of the Redis-backed meeting system.

- A test user is created in the SQL database.
- A single meeting ("m1") is created that is currently active and includes the test user as a participant.
- The scheduler is run once to activate the meeting in Redis.
- The user then joins the meeting.
- The script verifies:
    - That the user can successfully join the active meeting
    - That the meeting is correctly detected as nearby (within 100m)
    - That the user can post a chat message
    - That chat history and user-specific messages are correctly stored and retrieved
    - That user chat logs from a specific meeting can be isolated
    - That ending the meeting logs users out and cleans up Redis state

This test confirms basic integration between the database, Redis, scheduler logic, chat system, and meeting lifecycle operations for a single user.
"""

# Step 0: Reset Redis State & Drop all tables (CAUTION: This will wipe all data) -> for testing purposes
r.flushdb()
Base.metadata.drop_all(bind=engine)

# Step 1: Init DB
init_db()
session = SessionLocal()

# Step 2: Create test user and meeting
user = User(email="test@example.com", name="Test", age=25, gender="M")
session.add(user)

meeting = Meeting(
    meetingID="m1",
    title="Test Meeting",
    description="Test Desc",
    t1=datetime.now(timezone.utc) - timedelta(minutes=1),
    t2=datetime.now(timezone.utc) + timedelta(minutes=30),
    lat=37.9838,
    long=23.7275,
    participants="test@example.com"
)
session.add(meeting)
session.commit()

# Step 3: Run scheduler once
activate_meetings()

# Step 4: Run join
print(join_meeting("test@example.com", "m1"))

# Step 5: Check nearby meetings
print(get_nearby_active_meetings("test@example.com", 37.9838, 23.7275))

# Step 6: Post message
print(post_message("test@example.com", "Hello from Redis!"))

# Step 7: Read chat
print(get_chat("m1"))

# Step 8: User messages
print(get_user_messages("test@example.com"))

# Step 9: User-specific chat
print(show_user_chat_in_meeting("test@example.com"))

# Step 10: End meeting
print(end_meeting("m1"))

session.close()