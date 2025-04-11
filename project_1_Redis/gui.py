import customtkinter as ctk
import requests
import threading
import time

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("800x600")
app.title("Redis Meeting App")

API_URL = "http://127.0.0.1:5000"

# Utility to clear entries
def clear_entries(*entries):
    for entry in entries:
        entry.delete(0, ctk.END)

# Utility to auto-hide labels
def flash_label(label, text, duration=3):
    label.configure(text=text)
    def clear():
        time.sleep(duration)
        label.configure(text="")
    threading.Thread(target=clear, daemon=True).start()

# Tabs
container = ctk.CTkFrame(master=app)
container.pack(padx=20, pady=20, fill="both", expand=True)

tabview = ctk.CTkTabview(master=container)
tabview.pack(fill="both", expand=True)

user_tab = tabview.add("Users")
meeting_tab = tabview.add("Meetings")
action_tab = tabview.add("Actions")
chat_tab = tabview.add("Chat")

# --- User Tab ---
ctk.CTkLabel(user_tab, text="Email").pack(pady=5)
email_entry = ctk.CTkEntry(user_tab)
email_entry.pack()

ctk.CTkLabel(user_tab, text="Name").pack(pady=5)
name_entry = ctk.CTkEntry(user_tab)
name_entry.pack()

ctk.CTkLabel(user_tab, text="Age").pack(pady=5)
age_entry = ctk.CTkEntry(user_tab)
age_entry.pack()

ctk.CTkLabel(user_tab, text="Gender").pack(pady=5)
gender_entry = ctk.CTkEntry(user_tab)
gender_entry.pack()

user_label = ctk.CTkLabel(user_tab, text="")
user_label.pack(pady=5)

def create_user():
    try:
        data = {
            "email": email_entry.get(),
            "name": name_entry.get(),
            "age": int(age_entry.get()),
            "gender": gender_entry.get()
        }
        r = requests.post(f"{API_URL}/create_user", json=data)
        if r.headers.get("Content-Type", "").startswith("application/json"):
            flash_label(user_label, r.json().get("message", "OK"))
        else:
            flash_label(user_label, f"Server error: {r.status_code}")
        clear_entries(email_entry, name_entry, age_entry, gender_entry)
    except Exception as e:
        flash_label(user_label, f"Error: {e}")

ctk.CTkButton(user_tab, text="Create User", command=create_user).pack(pady=10)

# --- Meeting Tab ---
meeting_entries = []
for label in ["Meeting ID", "Title", "Description", "Start Time (YYYY-MM-DD HH:MM)", "End Time (YYYY-MM-DD HH:MM)", "Latitude", "Longitude", "Participants (comma-separated emails)"]:
    ctk.CTkLabel(meeting_tab, text=label).pack(pady=3)
    entry = ctk.CTkEntry(meeting_tab)
    entry.pack()
    meeting_entries.append(entry)

meeting_label = ctk.CTkLabel(meeting_tab, text="")
meeting_label.pack(pady=5)

def create_meeting():
    try:
        data = {
            "meetingID": meeting_entries[0].get(),
            "title": meeting_entries[1].get(),
            "description": meeting_entries[2].get(),
            "t1": meeting_entries[3].get() + ":00",
            "t2": meeting_entries[4].get() + ":00",
            "lat": float(meeting_entries[5].get()),
            "long": float(meeting_entries[6].get()),
            "participants": meeting_entries[7].get()
        }
        r = requests.post(f"{API_URL}/create_meeting", json=data)
        flash_label(meeting_label, r.json().get("message", "OK"))
        clear_entries(*meeting_entries)
    except Exception as e:
        flash_label(meeting_label, f"Error: {e}")

def delete_meeting():
    try:
        data = {"meetingID": meeting_entries[0].get()}
        r = requests.post(f"{API_URL}/delete_meeting", json=data)
        flash_label(meeting_label, r.json().get("message", "OK"))
    except Exception as e:
        flash_label(meeting_label, f"Error: {e}")

ctk.CTkButton(meeting_tab, text="Create Meeting", command=create_meeting).pack(pady=5)
ctk.CTkButton(meeting_tab, text="Delete Meeting", command=delete_meeting).pack(pady=5)

# --- Actions Tab ---
ctk.CTkLabel(action_tab, text="Email").pack(pady=5)
action_email_entry = ctk.CTkEntry(action_tab)
action_email_entry.pack()

ctk.CTkLabel(action_tab, text="Meeting ID").pack(pady=5)
action_meeting_entry = ctk.CTkEntry(action_tab)
action_meeting_entry.pack()

action_label = ctk.CTkLabel(action_tab, text="")
action_label.pack(pady=5)

def call_action(endpoint):
    try:
        data = {
            "email": action_email_entry.get(),
            "meetingID": action_meeting_entry.get()
        }
        if endpoint == "end_meeting":
            data = {"meetingID": data["meetingID"]}
        r = requests.post(f"{API_URL}/{endpoint}", json=data)
        flash_label(action_label, r.json().get("message", "OK"))
        clear_entries(action_email_entry, action_meeting_entry)
    except Exception as e:
        flash_label(action_label, f"Error: {e}")

def show_active():
    try:
        r = requests.get(f"{API_URL}/active_meetings")
        active = r.json().get("active_meetings", [])
        flash_label(action_label, "Active: " + ", ".join(active))
    except Exception as e:
        flash_label(action_label, f"Error: {e}")

ctk.CTkButton(action_tab, text="Join Meeting", command=lambda: call_action("join")).pack(pady=2)
ctk.CTkButton(action_tab, text="Leave Meeting", command=lambda: call_action("leave")).pack(pady=2)
ctk.CTkButton(action_tab, text="End Meeting", command=lambda: call_action("end_meeting")).pack(pady=2)
ctk.CTkButton(action_tab, text="Show Active Meetings", command=show_active).pack(pady=5)

# --- Chat Tab ---
ctk.CTkLabel(chat_tab, text="Email").pack(pady=5)
chat_email_entry = ctk.CTkEntry(chat_tab)
chat_email_entry.pack()

ctk.CTkLabel(chat_tab, text="Message").pack(pady=5)
message_entry = ctk.CTkEntry(chat_tab)
message_entry.pack()

chat_label = ctk.CTkLabel(chat_tab, text="")
chat_label.pack(pady=5)
chat_output = ctk.CTkLabel(chat_tab, text="", justify="left")
chat_output.pack(padx=10, pady=10)

def post_message():
    try:
        data = {
            "email": chat_email_entry.get(),
            "message": message_entry.get()
        }
        r = requests.post(f"{API_URL}/post_message", json=data)
        flash_label(chat_label, r.json().get("message", "OK"))
        clear_entries(message_entry)
    except Exception as e:
        flash_label(chat_label, f"Error: {e}")

def get_chat():
    try:
        mid = action_meeting_entry.get()
        r = requests.get(f"{API_URL}/get_chat", params={"meetingID": mid})
        messages = r.json().get("messages", [])
        chat_output.configure(text="\n".join(f"{m['email']}: {m['message']}" for m in messages))
    except Exception as e:
        flash_label(chat_label, f"Error: {e}")

def get_user_messages():
    try:
        email = chat_email_entry.get()
        r = requests.get(f"{API_URL}/user_messages", params={"email": email})
        messages = r.json().get("messages", [])
        chat_output.configure(text="\n".join(m["message"] for m in messages))
    except Exception as e:
        flash_label(chat_label, f"Error: {e}")

ctk.CTkButton(chat_tab, text="Post Message", command=post_message).pack(pady=2)
ctk.CTkButton(chat_tab, text="Get Full Chat", command=get_chat).pack(pady=2)
ctk.CTkButton(chat_tab, text="My Messages", command=get_user_messages).pack(pady=5)

app.mainloop()