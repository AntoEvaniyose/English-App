import random
from app.db.session import redis_client

OTP_EXPIRY_SECONDS = 300  # 5 minutes


def generate_otp(email: str) -> str:
    otp = str(random.randint(100000, 999999))

    redis_client.setex(
        f"otp:{email}",
        OTP_EXPIRY_SECONDS,
        otp
    )

    return otp


def verify_otp(email: str, otp) -> bool:
    key = f"otp:{email}"
    stored = redis_client.get(key)

    if not stored:
        return False

    # 🔥 FIX: convert both to string
    if stored != str(otp):
        return False

    redis_client.delete(key)
    return True
