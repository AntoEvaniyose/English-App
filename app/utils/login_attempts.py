from app.db.session import redis_client

MAX_ATTEMPTS = 3
BLOCK_TIME = 300  # 5 min


def is_blocked(ip: str):
    if redis_client.exists(f"block:{ip}"):
        ttl = redis_client.ttl(f"block:{ip}")
        
        minutes, seconds = divmod(ttl, 60)

        return True, f"Too many failed attempts. Try again after {minutes}m {seconds}s."


    return False, None


def increment_attempts(ip: str):
    key = f"attempts:{ip}"
    attempts = redis_client.incr(key)

    if attempts == 1:
        redis_client.expire(key, BLOCK_TIME)

    if attempts >= MAX_ATTEMPTS:
        redis_client.setex(f"block:{ip}", BLOCK_TIME, "blocked")

    return attempts


def reset_attempts(ip: str):
    redis_client.delete(f"attempts:{ip}")
    redis_client.delete(f"block:{ip}")