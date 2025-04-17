import subprocess
import time
import requests

# Start Docker containers
subprocess.Popen(["docker-compose", "up", "--build", "-d"])

# Wait a bit for the Flask API to become reachable
def wait_for_api(url, retries=10, delay=3):
    time.sleep(5)  # Wait a bit more for the API to be ready
    for i in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(delay) # Wait a bit before checking if the API is ready
    return False

# Check API health
if wait_for_api("http://127.0.0.1:5000/health"):
    print("API is ready. Launching GUI...")
    subprocess.run(["python", "gui/gui.py"])
else:
    print("API did not respond in time.")