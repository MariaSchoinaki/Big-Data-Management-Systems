import os
import redis
import socket

def detect_redis_host():
    """Auto-detect if running locally or inside Docker."""
    try:
        # Try to resolve 'redis' (docker-compose service name)
        socket.gethostbyname("redis")
        return "redis"  # redis container is reachable : Default redis host name
    except socket.gaierror:
        return "localhost"  # fallback for local testing

REDIS_HOST = detect_redis_host()
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True,
    retry_on_timeout=True,
)
