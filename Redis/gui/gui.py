import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from dateutil import tz, parser
import customtkinter as ctk
import requests
import threading
import time
from gui.gui_utils import *

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.state("zoomed")
app.geometry("1000x600")
app.title("Redis Meeting App")

API_URL = "http://127.0.0.1:5000"

# Utility to enable/disable GUI widgets
def set_widgets_state(state):
    """Enable or disable key GUI widgets."""
    for widget in [create_user_button, create_meeting_button, join_button, leave_button, end_button,
                   show_active_button, show_nearby_button, post_message_button, get_chat_button, my_messages_button]:
        widget.configure(state=state)

# Utility to monitor backend
def monitor_backend():
    """Repeatedly check if backend API is up."""
    while True:
        try:
            r = requests.get(f"{API_URL}/health", timeout=2)
            if r.status_code == 200:
                flash_label(user_label, "✅ Backend is Online!", duration=5)
                set_widgets_state("normal")  # Enable everything
                break
        except Exception:
            flash_label(user_label, "❌ Waiting for Backend...", duration=2)
            set_widgets_state("disabled")  # Disable everything
        time.sleep(2)

# Utility to display long output
def display_long_output(target_label, lines):
    """Display lines in the correct label."""
    target_label.configure(text="\n".join(lines))
    
# Tabs
container = ctk.CTkScrollableFrame(master=app)
container.pack(padx=20, pady=20, fill="both", expand=True)

tabview = ctk.CTkTabview(master=container)
tabview.pack(padx=10, pady=10, fill="both", expand=True)

user_tab = tabview.add("Users")
meeting_tab = tabview.add("Meetings")
action_tab = tabview.add("Actions")
chat_tab = tabview.add("Chat")

# --- User Tab ---
ctk.CTkLabel(user_tab, text="Email").pack(pady=5)
email_entry = ctk.CTkEntry(user_tab); email_entry.pack()
ctk.CTkLabel(user_tab, text="Name").pack(pady=5)
name_entry = ctk.CTkEntry(user_tab); name_entry.pack()
ctk.CTkLabel(user_tab, text="Age").pack(pady=5)
age_entry = ctk.CTkEntry(user_tab); age_entry.pack()
ctk.CTkLabel(user_tab, text="Gender").pack(pady=5)
gender_entry = ctk.CTkEntry(user_tab); gender_entry.pack()
user_label = ctk.CTkLabel(user_tab, text=""); user_label.pack(pady=5)

def create_user():
    if not validate_entries(email_entry, name_entry, age_entry, gender_entry):
        flash_label(user_label, "⚠️ Please fill in all fields.")
        return
        
    email = email_entry.get().strip().lower() # Force lowercase
    name = name_entry.get().strip()
    age_str = age_entry.get().strip()
    gender = gender_entry.get().strip()

    # Email validation
    if not is_valid_email(email):
        flash_label(user_label, "❌ Please enter a valid email address.")
        return

    # Name validation (only letters)
    if not name.isalpha():
        flash_label(user_label, "❌ Name must only contain alphabetic characters.")
        return

    # Age validation
    if not age_str.isdigit():
        flash_label(user_label, "❌ Age must be a number.")
        return
    if int(age_str) < 18:
        flash_label(user_label, "❌ Age must be at least 18 years old.")
        return

    try:
        data = {
            "email": email,
            "name": name,
            "age": int(age_str),
            "gender": gender
        }
        r = requests.post(f"{API_URL}/create_user", json=data)
        msg = r.json().get("message", "OK")
        flash_label(user_label, msg)
        clear_entries(email_entry, name_entry, age_entry, gender_entry)
    except ValueError:
        flash_label(user_label, "⚠️ Age must be a valid number.")
    except Exception as e:
        flash_label(user_label, f"Error: Try again.") # {e}

create_user_button = ctk.CTkButton(user_tab, text="Create User", command=create_user)
create_user_button.pack(pady=10)

# --- Meeting Tab ---
meeting_fields = ["Title", "Description", "Start Time (YYYY-MM-DD HH:MM)", 
                  "End Time (YYYY-MM-DD HH:MM)", "Latitude", "Longitude", 
                  "Participants (comma‑sep emails)"]
meeting_entries = []
for label in meeting_fields:
    ctk.CTkLabel(meeting_tab, text=label).pack(pady=3)
    entry = ctk.CTkEntry(meeting_tab)
    entry.pack()
    meeting_entries.append(entry)
    
# Pre-fill with current time
reset_datetime_fields(meeting_entries[2], meeting_entries[3])

meeting_label = ctk.CTkLabel(meeting_tab, text=""); meeting_label.pack(pady=5)

def create_meeting():
    # === Manual Input Validation ===
    if not validate_entries(*meeting_entries):
        flash_label(meeting_label, "⚠️ Please fill in all meeting fields.")
        return
        
    title = meeting_entries[0].get().strip()
    description = meeting_entries[1].get().strip()
    
    participants_csv = meeting_entries[6].get()

    # Safer list creation
    participants_raw = participants_csv if isinstance(participants_csv, list) else participants_csv.split(",")
    
    # Clean processing
    participants = []
    for email in participants_raw:
        email = email.strip()
        if email and is_valid_email(email):
            participants.append(email.lower())  # normalize to lowercase
    
    # Deduplicate
    participants = list(set(participants))
    
    # Final Check
    if not participants or len(participants) < 2:
        flash_label(meeting_label, "⚠️ Please provide at least 2 valid, unique participant emails.")
        return

    start_input = meeting_entries[2].get()
    end_input = meeting_entries[3].get()

    try:
        # === Risky Parsing ===
        local = tz.gettz("Europe/Athens")
        now = datetime.now(local)

        start_dt = datetime.strptime(start_input, "%Y-%m-%d %H:%M").replace(tzinfo=local)
        end_dt = datetime.strptime(end_input, "%Y-%m-%d %H:%M").replace(tzinfo=local)

        if start_dt >= end_dt:
            flash_label(meeting_label, "⚠️ End time must be after start time.")
            return

        lat = float(meeting_entries[4].get())
        lon = float(meeting_entries[5].get())

        if not (-90 <= lat <= 90):
            flash_label(meeting_label, "⚠️ Latitude must be between -90 and 90.")
            clear_entries(meeting_entries[4]) # Clear invalid lat
            return
        if not (-180 <= lon <= 180):
            flash_label(meeting_label, "⚠️ Longitude must be between -180 and 180.")
            clear_entries(meeting_entries[5]) # Clear invalid lon
            return

        if (now - start_dt).total_seconds() > 300:
            flash_label(meeting_label, "❕Start time was too early. Reset to now. Please review times and click again.")
            reset_datetime_fields(meeting_entries[2], meeting_entries[3])
            return
        
        # === Server Communication ===
        payload = {
            "title": title,
            "description": description,
            "t1": start_dt.strftime("%Y-%m-%d %H:%M") + ":00",
            "t2": end_dt.strftime("%Y-%m-%d %H:%M") + ":00",
            "lat": lat,
            "long": lon,
            "participants": participants
        }

        r = requests.post(f"{API_URL}/create_meeting", json=payload)
        resp = r.json()
        if resp.get("status") == "success":
            new_id = resp.get("meetingID")
            flash_label(meeting_label, f"Created Meeting {title} with ID {new_id}")
            action_meeting_entry.delete(0, ctk.END)
            action_meeting_entry.delete(0, ctk.END)
            requests.post(f"{API_URL}/force_scheduler")
            clear_entries(*meeting_entries)
            reset_datetime_fields(meeting_entries[2], meeting_entries[3])
        else:
            flash_label(meeting_label, resp.get("message", "Error"))
    except ValueError:
        flash_label(meeting_label, "⚠️ Date/time/coordinates must be in correct format.")
    except Exception as e:
        print(f"Error in create_meeting: {e}")
        flash_label(meeting_label, f"Error: Try again.") # {e}    

create_meeting_button = ctk.CTkButton(meeting_tab, text="Create Meeting", command=create_meeting)
create_meeting_button.pack(pady=5)

# --- Actions Tab ---
ctk.CTkLabel(action_tab, text="Email").pack(pady=5)
action_email_entry = ctk.CTkEntry(action_tab); action_email_entry.pack()
ctk.CTkLabel(action_tab, text="Meeting ID").pack(pady=5)
action_meeting_entry = ctk.CTkEntry(action_tab); action_meeting_entry.pack()
action_label = ctk.CTkLabel(action_tab, text=""); action_label.pack(pady=5)

def call_action(endpoint):
    email = action_email_entry.get().strip()
    meeting_id = action_meeting_entry.get().strip()

    # Basic Validation
    if endpoint != "end_meeting" and not email:
        flash_label(action_label, "❌ Email is required.")
        return

    if not meeting_id:
        flash_label(action_label, "⚠️ Please enter Meeting ID.")
        return

    if not meeting_id.isdigit():
        flash_label(action_label, "❌ Meeting ID must be a valid number.")
        return

    try:
        data = {"meetingID": int(meeting_id)}
        if endpoint != "end_meeting":
            data["email"] = email

        r = requests.post(f"{API_URL}/{endpoint}", json=data)
        if r.status_code == 200:
            flash_label(action_label, r.json().get("message", "OK"), 10)
            clear_entries(action_email_entry, action_meeting_entry)
    except Exception as e:
        print(f"Error in call_action/{endpoint}: {e}")
        flash_label(action_label, f"Error: Try again.")

def show_active():
    try:
        r = requests.get(f"{API_URL}/active_meetings")
        lst = r.json().get("active_meetings", [])
        if len(lst) > 0:
            lines = ["🤝 All Active Meetings:\n"]
            for m in lst:
                start_time = format_meeting_time(m['t1'])
                end_time = format_meeting_time(m['t2'])
                participants = format_participants(m.get("participants", ""))

                lines.append(
                    f"- ℹ️ Meeting Info: {m['title']} (ID {m['id']}) | ⏰ Duration: {start_time} → {end_time} | 🌐 Location (lat, long): {m['lat']}, {m['long']} | 💼 Participants: {participants}"
                )
            display_long_output(action_output, lines)
        else:
            display_long_output(action_output, ["⚠️ No active meetings currently available."])
    except Exception as e:
        flash_label(action_label, f"Error: Try again.") # {e}

def show_nearby_active():
    try:
        if not validate_entries(show_nearby_user_email_entry, show_nearby_user_lat_entry, show_nearby_user_long_entry):
            flash_label(action_label, "⚠️ Please fill in all fields.")
            return

        r = requests.get(
            f"{API_URL}/get_nearby",
            params={
                "email": show_nearby_user_email_entry.get().strip(),
                "lat": float(show_nearby_user_lat_entry.get().strip()),
                "long": float(show_nearby_user_long_entry.get().strip())
            }
        )

        if r.status_code == 404:
            flash_label(action_label, "❌ User not found. Please check the email address.")
            clear_entries(show_nearby_user_email_entry)
            return
        elif r.status_code != 200:
            flash_label(action_label, f"⚠️ Error fetching nearby meetings (Status {r.status_code})")
            clear_entries(show_nearby_user_email_entry, show_nearby_user_lat_entry, show_nearby_user_long_entry)
            return

        lst = r.json().get("active_meetings", [])
        if len(lst) > 0:
            lines = [f"📍 Nearby Active Meetings that {show_nearby_user_email_entry.get().strip()} can join:\n"]
            for m in lst:
                start_time = format_meeting_time(m['t1'])
                end_time = format_meeting_time(m['t2'])
                participants = format_participants(m.get("participants", ""))
                lines.append(
                    f"- ℹ️ Meeting Info: {m['title']} (ID {m['id']}) | ⏰ Duration: {start_time} → {end_time} | 📏 Distance: {m['distance_meters']}m away | 🌐 Location (lat, long): {m['lat']}, {m['long']} |💼 Participants: {participants}"
                )
            display_long_output(action_output, lines)
        else:
            display_long_output(action_output, ["⚠️ No nearby active meetings found."])

        clear_entries(show_nearby_user_email_entry, show_nearby_user_lat_entry, show_nearby_user_long_entry)
    except Exception as e:
        print(f"Error in show_nearby_active: {e}")
        flash_label(action_label, f"Error: Try again.")

def get_all_users():
    try:
        r = requests.get(f"{API_URL}/get_all_users")
        emails = r.json().get("emails", [])
        if emails and len(emails) > 0:
            lines = ["📋 Registered Users:"]
            lines.extend([f"- {email}" for email in emails])
            display_long_output(user_output, lines)
        else:
            display_long_output(user_output, ["⚠️ No users found."])
    except Exception as e:
        print(f"Error in get_all_users: {e}")
        flash_label(action_label, f"Error: Try again.")  # {e}

join_button = ctk.CTkButton(action_tab, text="Join Meeting", command=lambda: call_action("join"))
join_button.pack(pady=2)
leave_button = ctk.CTkButton(action_tab, text="Leave Meeting", command=lambda: call_action("leave"))
leave_button.pack(pady=2)
end_button = ctk.CTkButton(action_tab, text="End Meeting", command=lambda: call_action("end_meeting"))
end_button.pack(pady=2)

show_active_button = ctk.CTkButton(action_tab, text="Show Active Meetings", command=show_active)
show_active_button.pack(pady=5)

ctk.CTkLabel(action_tab, text="Email").pack(pady=5)
show_nearby_user_email_entry = ctk.CTkEntry(action_tab); show_nearby_user_email_entry.pack()
ctk.CTkLabel(action_tab, text="Latitude").pack(pady=5)
show_nearby_user_lat_entry = ctk.CTkEntry(action_tab); show_nearby_user_lat_entry.pack()
ctk.CTkLabel(action_tab, text="Longitude").pack(pady=5)
show_nearby_user_long_entry = ctk.CTkEntry(action_tab); show_nearby_user_long_entry.pack()

show_nearby_button = ctk.CTkButton(action_tab, text="Find Nearby Active Meetings", command=show_nearby_active)
show_nearby_button.pack(pady=5)
action_output = ctk.CTkLabel(action_tab, text="", justify="left")
action_output.pack(padx=10, pady=10)

get_users_button = ctk.CTkButton(action_tab, text="Get All Users", command=get_all_users)
get_users_button.pack(pady=5)
user_output = ctk.CTkLabel(action_tab, text="", justify="left")
user_output.pack(padx=10, pady=10)

# --- Chat Tab ---
ctk.CTkLabel(chat_tab, text="Meeting ID").pack(pady=5)
chat_meeting_entry = ctk.CTkEntry(chat_tab); chat_meeting_entry.pack()
ctk.CTkLabel(chat_tab, text="Email").pack(pady=5)
chat_email_entry = ctk.CTkEntry(chat_tab); chat_email_entry.pack()
ctk.CTkLabel(chat_tab, text="Message").pack(pady=5)
message_entry = ctk.CTkEntry(chat_tab); message_entry.pack()
chat_label = ctk.CTkLabel(chat_tab, text=""); chat_label.pack(pady=5)
chat_output = ctk.CTkLabel(chat_tab, text="", justify="left"); chat_output.pack(padx=10, pady=10)

def post_message():
    if not validate_entries(chat_email_entry, chat_meeting_entry, message_entry):
        flash_label(chat_label, "⚠️ Please fill Email, Meeting ID, and Message.")
        return

    try:
        meeting_id = chat_meeting_entry.get()
        if not meeting_id.isdigit():
            flash_label(chat_label, "❌ Meeting ID must be a number.")
            clear_entries(chat_meeting_entry)
            return

        data = {
            "email": chat_email_entry.get().strip(),
            "message": message_entry.get().strip(),
            "meetingID": meeting_id
        }
        r = requests.post(f"{API_URL}/post_message", json=data)

        if r.status_code == 400:
            flash_label(chat_label, r.json().get("message", "❌ Error sending message."))
        elif r.status_code == 200:
            flash_label(chat_label, r.json().get("message", "✅ Message posted."))
            clear_entries(chat_email_entry, message_entry, chat_meeting_entry)
        else:
            flash_label(chat_label, f"⚠️ Unexpected error (Status {r.status_code}).")
    except Exception as e:
        print(f"Error in post_message: {e}")
        flash_label(chat_label, f"Error: Try again.")  # {e}

def get_chat():
    try:
        mid = chat_meeting_entry.get()
        r = requests.get(f"{API_URL}/get_chat", params={"meetingID": mid})
        msgs = r.json().get("messages", [])
        if len(msgs) > 0:
            lines = [f"📋 Chat of Meeting {mid}:\n"]
            lines.extend([
                f"[{parser.isoparse(m['timestamp']).strftime('%Y-%m-%d %H:%M')}] {m['email']} --- {m['message']}"
                for m in msgs
            ])
            display_long_output(chat_output, lines)
        else:
            display_long_output(chat_output, ["⚠️ No messages found for this meeting yet."])
        clear_entries(chat_meeting_entry)
    except ValueError:
        flash_label(chat_label, "❌ Meeting ID must be a number.")
    except Exception as e:
        print(f"Error in get_chat: {e}")
        flash_label(chat_label, f"Error: Try again.")  # {e}

def get_user_messages():
    try:
        email = chat_email_entry.get().strip()
        if not email:
            flash_label(chat_label, "❌ Please enter your Email to fetch your messages.")
            return

        r = requests.get(f"{API_URL}/user_messages", params={"email": email})
        msgs = r.json().get("messages", [])
        if len(msgs) > 0:
            lines = [f"📋 Messages posted by {email}:\n"]
            for m in msgs:
                timestamp = parser.isoparse(m["timestamp"]).strftime("%H:%M") if "timestamp" in m else "--:--"
                lines.append(f"[{timestamp}] {m['message']} | in Meeting {m['title']} (ID {m['meetingID']})")
            display_long_output(chat_output, lines)
        else:
            display_long_output(chat_output, [f"⚠️ {email} has not posted any messages yet."])
        clear_entries(chat_email_entry)
    except Exception as e:
        print(f"Error in get_user_messages: {e}")
        flash_label(chat_label, "⚠️ Error: Try again.")  # {e}

post_message_button = ctk.CTkButton(chat_tab, text="Post Message", command=post_message)
post_message_button.pack(pady=2)
get_chat_button = ctk.CTkButton(chat_tab, text="Get Full Chat", command=get_chat)
get_chat_button.pack(pady=2)
my_messages_button = ctk.CTkButton(chat_tab, text="My Messages", command=get_user_messages)
my_messages_button.pack(pady=5)

# def force_run_scheduler():
#     try:
#         r = requests.post(f"{API_URL}/force_scheduler")
#         flash_label(action_label, "Scheduler ran manually!")
#     except Exception as e:
#         flash_label(action_label, f"Error: {e}")

# ctk.CTkButton(action_tab, text="Force Run Scheduler", command=force_run_scheduler, bg_color="red").pack(pady=2)

def main():
    try:
        threading.Thread(target=monitor_backend, daemon=True).start()
        app.mainloop()
    except Exception as e:
        print(f"Fatal GUI Error: {e}")

if __name__ == "__main__":
    main()