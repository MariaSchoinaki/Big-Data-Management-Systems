import os
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")   # default to the docker‐compose service name
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True,
    retry_on_timeout=True,
)
