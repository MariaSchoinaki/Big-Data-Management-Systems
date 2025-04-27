import os
import sys
import subprocess
import time

# Insert the project root (one level up) onto sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.launch_utils import wait_for_containers_ready, wait_for_api, stop_docker_containers

try:
    print("🚀 Starting Docker Compose...")
    subprocess.Popen(["docker-compose", "up", "--build", "-d"])

    # Step 1: Wait for containers to appear
    if not wait_for_containers_ready(["project_1_redis-redis-1", "project_1_redis-web-1"]):
        print("❌ Containers failed to start.")
        sys.exit(1)
        
    time.sleep(20) # Docker Containers take about 15-20 seconds to finish building
    
    # Step 2: Wait for Flask API to become reachable
    print("⏳ Waiting for API to become healthy...")
    if not wait_for_api("http://127.0.0.1:5000/health"):
        print("❌ API did not become healthy.")
        sys.exit(1)

    print("✅ Backend is ready. Launching GUI...")
    # Step 3: Launch GUI with venv python
    gui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "gui", "gui.py"))
    venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "python.exe"))

    gui_process = subprocess.Popen([venv_python, gui_path], stderr=subprocess.STDOUT)

    # Step 4: Wait for GUI to close
    gui_process.wait()

finally:
    # Step 5: Always clean up Docker containers when done
    stop_docker_containers()