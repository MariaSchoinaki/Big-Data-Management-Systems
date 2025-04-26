import customtkinter as ctk
import requests
import threading
from datetime import datetime, timedelta, timezone
from dateutil import tz
import time

# Utility to clear entries
def clear_entries(*entries):
    for entry in entries:
        entry.delete(0, ctk.END)

# Utility to auto-hide labels
def flash_label(label, text, duration=5):
    label.configure(text=text)
    def clear():
        time.sleep(duration)
        label.configure(text="")
    threading.Thread(target=clear, daemon=True).start()

# Validation Utility
def validate_entries(*entries):
    """Returns True if all fields are filled, False if any field is empty."""
    for entry in entries:
        if not entry.get().strip():
            return False
    return True
    
# Utility to reset time fields
def reset_datetime_fields(start_entry, end_entry):
    """Clears and repopulates the start and end time entries with Greek local time now and now+2h."""
    local = tz.gettz("Europe/Athens") # or tz.tzlocal() if you prefer dynamic
    now = datetime.now(local)
    start = now.strftime("%Y-%m-%d %H:%M")
    end = (now + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")

    start_entry.delete(0, ctk.END)
    start_entry.insert(0, start)

    end_entry.delete(0, ctk.END)
    end_entry.insert(0, end)

# Utility to format meeting time
def format_meeting_time(utc_dt_str):
    """Format UTC datetime string to Greek local time."""
    utc_dt = datetime.strptime(utc_dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    greek_time = utc_dt.astimezone(tz.gettz('Europe/Athens'))
    return greek_time.strftime("%Y-%m-%d %H:%M")