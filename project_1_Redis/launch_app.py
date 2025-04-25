import os, sys, time, subprocess

# Insert the project root (one level up) onto sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Starts Docker container
print("Starting Docker Compose...")
subprocess.Popen(["docker-compose", "up", "--build", "-d"])

# Waits until the Flask API is reachable
from src.utils import wait_for_api
print("Waiting for API to become ready...")
# Wait for API then launch GUI in a truly separate process
if wait_for_api("http://127.0.0.1:5000/health"):
    print("API is healthy.")
    time.sleep(5)
    gui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "gui", "gui.py"))
    print(f"Launching GUI from: {gui_path}")
    subprocess.Popen(["cmd", "/k", "python", gui_path])
else:
    print("API did not respond in time.")