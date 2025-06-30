import time
import threading
from datetime import datetime, timedelta
from dateutil import tz
import customtkinter as ctk

# === GUI Utility Functions ===

def validate_entries(*entries):
    """Ensure all given entries have non-empty values."""
    for entry in entries:
        if not entry.get().strip():
            return False
    return True

def clear_entries(*entries):
    """Clear given Entry widgets."""
    for entry in entries:
        entry.delete(0, ctk.END)

def flash_label(label, text, duration=6):
    """Display a temporary message on a label."""
    label.configure(text=text)
    def clear():
        time.sleep(duration)
        label.configure(text="")
    threading.Thread(target=clear, daemon=True).start()

def reset_datetime_fields(start_entry, end_entry):
    """Resets start and end fields to Greek local time now and now+2h."""
    local = tz.gettz("Europe/Athens")
    now = datetime.now(local)
    start = now.strftime("%Y-%m-%d %H:%M")
    end = (now + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")

    start_entry.delete(0, ctk.END)
    start_entry.insert(0, start)

    end_entry.delete(0, ctk.END)
    end_entry.insert(0, end)

def format_meeting_time(utc_dt_str):
    """Format a UTC datetime string into Greek local time."""
    utc_dt = datetime.strptime(utc_dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz.tzutc())
    greek_time = utc_dt.astimezone(tz.gettz('Europe/Athens'))
    return greek_time.strftime("%Y-%m-%d %H:%M")

def display_long_output(target_label, lines):
    """Helper to display long outputs cleanly."""
    target_label.configure(text="\n".join(lines))
    
def is_valid_email(email: str) -> bool:
    """Minimal serious email validation: one @, one ., correct order, no spaces, etc."""
    email = email.strip()
    if ' ' in email:
        return False
    if email.count('@') != 1 or email.count('.') < 1:
        return False
    if email.index('@') > email.rindex('.'):
        return False
    user, domain = email.split('@')
    if len(user) < 3:
        return False
    if len(domain.split('.')[-1]) < 2:
        return False
    return True
    
def format_participants_short(raw_participants):
    """
    Format a raw participants string into a user-friendly list.
    Shows up to 3 names, then "+X more..." if needed.
    """
    if not raw_participants:
        return "No participants"

    participant_list = [p.strip() for p in raw_participants.split(",") if p.strip()]
    if not participant_list:
        return "No participants"

    if len(participant_list) > 3:
        return ", ".join(participant_list[:3]) + f", +{len(participant_list) - 3} more..."
    else:
        return ", ".join(participant_list)
        
def format_participants(raw_participants):
    """
    Format a raw participants string into a user-friendly list.
    """
    if not raw_participants:
        return "No participants"

    participant_list = [p.strip() for p in raw_participants.split(",") if p.strip()]
    if not participant_list:
        return "No participants"

    return ", ".join(participant_list)