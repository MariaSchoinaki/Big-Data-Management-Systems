from db import Base, engine, init_db, SessionLocal, User, Meeting
from logic import *
from datetime import datetime, timezone, timedelta
# Step 0: Drop all tables (CAUTION: This will wipe all data) -> for testing purposes
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
from scheduler import activate_meetings
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