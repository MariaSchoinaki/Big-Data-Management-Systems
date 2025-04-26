# Utility functions
import subprocess
import requests
import time
import math
from datetime import datetime

# Decode redis set
def decode_redis_set(redis_set):
    """Decode Redis bytes to strings if needed."""
    return [item.decode() if isinstance(item, bytes) else item for item in redis_set]

# Haversine Distance formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

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
    print("\n🔻 Stopping Docker containers...")
    subprocess.run(["docker-compose", "down"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ Containers stopped.")