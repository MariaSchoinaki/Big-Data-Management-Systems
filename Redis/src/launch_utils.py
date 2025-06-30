import subprocess
import requests
import time

# Check if API is reachable
def wait_for_api(url, retries=10, delay=2):
    for i in range(retries):
        print(f"Checking API health... Attempt {i+1}")
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(delay)
    return False

# Wait for containers to start
def wait_for_containers_ready(container_names, timeout=60):
    """Wait until all given containers are running."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)
        running_containers = result.stdout.splitlines()
        if all(name in running_containers for name in container_names):
            print("✅ Containers are running!")
            return True
        print("⏳ Waiting for containers to start...")
        time.sleep(2)
    print("❌ Containers did not start in time!")
    return False

# Stop Docker containers
def stop_docker_containers():
    print("\n🔻 Checking if Docker containers need stopping...")

    try:
        # Check if containers are still running
        result = subprocess.run(["docker", "ps", "--filter", "name=project_1_redis", "--format", "{{.Names}}"], capture_output=True, text=True)

        if result.stdout.strip() == "":
            print("✅ No project containers are running. Nothing to stop.")
            return

        # Otherwise, attempt to bring them down
        print("🛑 Containers detected. Running docker-compose down...")
        subprocess.run(["docker-compose", "down"], check=True)
        print("✅ Docker containers stopped successfully.")

    except Exception as e:
        print(f"❌ Failed during stopping containers: {e}")
    
