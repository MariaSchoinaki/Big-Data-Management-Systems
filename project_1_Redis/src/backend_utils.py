import math
from datetime import datetime, timezone

# === Backend Utilities ===

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def decode_redis_set(redis_set):
    """Decode Redis bytes to strings if needed."""
    return [item.decode() if isinstance(item, bytes) else item for item in redis_set]

def is_valid_email(email: str) -> bool:
    """Minimal serious email validation: one @, one ., correct order, no spaces, etc."""
    email = email.strip()
    if ' ' in email:
        return False
    if email.count('@') != 1 or email.count('.') < 1:
        return False
    if email.index('@') > email.rindex('.'):
        return False
    user, domain = email.split('@')
    if len(user) < 3:
        return False
    if len(domain.split('.')[-1]) < 2:
        return False
    return True

def format_datetime_to_greek_local(utc_dt_str):
    from dateutil import tz
    utc_dt = datetime.strptime(utc_dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    greek_time = utc_dt.astimezone(tz.gettz('Europe/Athens'))
    return greek_time.strftime("%Y-%m-%d %H:%M")