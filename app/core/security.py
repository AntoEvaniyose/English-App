from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.responses import CustomResponse
from app.db.models.admin import Admin, AdminRefreshToken
from app.db.models.user import User,UserRefreshToken


# =======================
# PASSWORD HASHING
# =======================
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# =======================
# TOKEN HELPERS
# =======================
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _create_token(data: dict, expires_minutes: int) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4()),
    })

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["type"] = "access"
    return _create_token(payload, settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    payload["type"] = "refresh"
    return _create_token(payload, settings.REFRESH_TOKEN_EXPIRE_DAYS * 1440)


# =======================
# COMMON VALIDATION
# =======================
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def _credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )


# =======================
# REFRESH TOKEN CORE LOGIC
# =======================
def _handle_refresh(
    *,
    refresh_token: str,
    db: Session,
    user_obj,
    role: str,
    is_admin: bool = False
):
    payload = decode_token(refresh_token)

    # ✅ Validate token type
    if payload.get("type") != "refresh":
        raise _credentials_exception()

    # 🔥 FIX: use user_id instead of username
    user_id = payload.get("sub")
    token_version = payload.get("token_version")

    if not user_id:
        raise _credentials_exception()

    # ✅ Validate user/admin existence
    if not user_obj or not user_obj.is_active:
        raise _credentials_exception()

    # ✅ Ensure token belongs to same user
    if str(user_obj.id) != str(user_id):
        raise _credentials_exception()

    # ✅ Token version check (global logout support)
    if token_version != getattr(user_obj, "token_version", 0):
        raise _credentials_exception()

    # 🔐 Hash token
    token_hash = hash_token(refresh_token)

    # ✅ Select correct model
    token_model = AdminRefreshToken if is_admin else UserRefreshToken

    # ✅ Validate token in DB
    if is_admin:
        token_entry = db.query(token_model).filter(
            token_model.token == token_hash,
            token_model.admin_id == user_obj.id,
            token_model.is_revoked == False
        ).first()
    else:
        token_entry = db.query(token_model).filter(
            token_model.token == token_hash,
            token_model.user_id == user_obj.id,
            token_model.is_revoked == False
        ).first()

    if not token_entry:
        raise _credentials_exception()

    # ⏳ Expiry check
    if token_entry.expires_at < datetime.now(timezone.utc):
        raise _credentials_exception()

    # 🔁 Revoke old token (rotation)
    token_entry.is_revoked = True

    # ===============================
    # 🔥 CREATE NEW TOKENS (FIXED)
    # ===============================
    new_access_token = create_access_token({
        "sub": str(user_obj.id),   # ✅ FIXED
        "id": user_obj.id,
        "role": role,
        "token_version": getattr(user_obj, "token_version", 0),
    })

    new_refresh_token = create_refresh_token({
        "sub": str(user_obj.id),   # ✅ FIXED
        "id": user_obj.id,
        "role": role,
        "token_version": getattr(user_obj, "token_version", 0),
    })

    # ===============================
    # 💾 STORE NEW REFRESH TOKEN
    # ===============================
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    if is_admin:
        new_entry = AdminRefreshToken(
            admin_id=user_obj.id,
            token=hash_token(new_refresh_token),
            expires_at=expires_at,
        )
    else:
        new_entry = UserRefreshToken(
            user_id=user_obj.id,
            token=hash_token(new_refresh_token),
            expires_at=expires_at,
        )

    db.add(new_entry)
    db.commit()

    # ===============================
    # ✅ RESPONSE
    # ===============================
    return CustomResponse.success(
        "Access token refreshed successfully",
        {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "role": role,
        }
    )

# =======================
# ADMIN REFRESH
# =======================
def refresh_access_token_admin(refresh_token: str, db: Session):
    payload = decode_token(refresh_token)

    user_id = payload.get("sub")

    admin = db.query(Admin).filter(
        Admin.id == user_id,
        Admin.is_active == True
    ).first()

    return _handle_refresh(
        refresh_token=refresh_token,
        db=db,
        user_obj=admin,
        role="admin",
        is_admin=True
    )


# =======================
# USER REFRESH
# =======================
def refresh_user_token(refresh_token: str, db: Session):
    payload = decode_token(refresh_token)

    user_id = payload.get("sub")

    user = db.query(User).filter(
        User.id == user_id,
        User.is_active == True
    ).first()

    return _handle_refresh(
        refresh_token=refresh_token,
        db=db,
        user_obj=user,
        role="user",
        is_admin=False
    )


# =======================
# LOGIN TOKEN CREATION
# =======================



def generate_login_tokens(user_obj, db: Session, role: str, is_admin=False):

    subject = str(user_obj.id)   # ✅ FIXED

    access_token = create_access_token({
        "sub": subject,
        "id": user_obj.id,
        "role": role,
        "token_version": getattr(user_obj, "token_version", 0),
    })

    refresh_token = create_refresh_token({
        "sub": subject,
        "id": user_obj.id,
        "role": role,
        "token_version": getattr(user_obj, "token_version", 0),
    })

    token_hash = hash_token(refresh_token)

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    if is_admin:
        token_entry = AdminRefreshToken(
            admin_id=user_obj.id,
            token=token_hash,
            expires_at=expires_at,
        )
    else:
        token_entry = UserRefreshToken(
            user_id=user_obj.id,
            token=token_hash,
            expires_at=expires_at,
        )

    db.add(token_entry)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": role,
    }


# =======================
# LOGOUT
# =======================
def logout(refresh_token: str, db: Session, is_admin: bool = False):
    try:
        token_hash = hash_token(refresh_token)

        token_model = AdminRefreshToken if is_admin else UserRefreshToken

        token = db.query(token_model).filter(
            token_model.token == token_hash,
            token_model.is_revoked == False
        ).first()

        if token:
            token.is_revoked = True
            db.commit()

        return CustomResponse.success("Logged out successfully")

    except Exception as e:
        print(f"Logout error: {e}")
        raise e  # or log properly
    

RESET_TOKEN_EXPIRE_MINUTES = 15

# =========================
# CREATE RESET TOKEN
# =========================
def create_password_reset_token(user):
    if user.password_changed_at is None:
        raise ValueError("password_changed_at must be set before creating reset token")

    payload = {
        "sub": user.email,
        "pwd_ts": int(user.password_changed_at.timestamp()),
        "type": "password_reset",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


# =========================
# VERIFY RESET TOKEN
# =========================
def verify_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])

        email = payload.get("sub")
        pwd_ts = payload.get("pwd_ts")

        if not email or not pwd_ts:
            return None, None

        return email, pwd_ts

    except JWTError:
        return None, None
    