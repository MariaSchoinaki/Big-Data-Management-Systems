import subprocess
import time

def ensure_redis_running():
    """Start Redis if not already running (using Docker)."""
    try:
        # Check if redis is already running
        result = subprocess.run(["docker", "ps", "--filter", "name=redis", "--format", "{{.Names}}"], capture_output=True, text=True)
        if "redis" not in result.stdout:
            print("🔵 Redis not running. Starting Redis container...")
            subprocess.run(["docker", "run", "-d", "--name", "redis", "-p", "6379:6379", "redis:7"], check=True)
            time.sleep(5)  # Wait a few seconds for Redis to fully start
        else:
            print("✅ Redis already running.")
    except Exception as e:
        print(f"❌ Failed to ensure Redis is running: {e}")
        
def stop_redis_container():
    """Stop and remove the Redis Docker container if it was started."""
    try:
        print("\n🔻 Stopping Redis container...")
        subprocess.run(["docker", "stop", "redis"], check=True)
        subprocess.run(["docker", "rm", "redis"], check=True)
        print("✅ Redis container stopped and removed.")
    except Exception as e:
        print(f"❌ Failed to stop Redis container: {e}")

