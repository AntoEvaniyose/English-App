from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.admin import Admin


# 🔐 Token extractor
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/user/login")


# ===============================
# 🔍 COMMON TOKEN DECODER
# ===============================
def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ===============================
# 👤 GET CURRENT USER
# ===============================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)

    user_id = payload.get("id")
    token_type = payload.get("type")
    token_version = payload.get("token_version")

    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    # 🔥 Token version check (logout support)
    if token_version != user.token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please login again."
        )

    return user


# ===============================
# 👑 GET CURRENT ADMIN
# ===============================
def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)

    user_id = payload.get("id")
    role = payload.get("role")
    token_type = payload.get("type")

    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    admin = db.query(Admin).filter(Admin.id == user_id).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found"
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin is inactive"
        )

    return admin


# ===============================
# 🔐 ROLE-BASED GUARDS
# ===============================

# ✅ Only logged-in users
def require_user(current_user: User = Depends(get_current_user)):
    if current_user.role.value != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User access required"
        )
    return current_user


# ✅ Only admins
def require_admin(current_admin: Admin = Depends(get_current_admin)):
    return current_admin


# ===============================
# 🔥 OPTIONAL FLEXIBLE ROLE GUARD
# ===============================
def require_role(required_role: str):
    def role_checker(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ):
        payload = decode_access_token(token)

        role = payload.get("role")
        user_id = payload.get("id")

        if role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role} access required"
            )

        # 🔁 Fetch from correct table
        if role == "admin":
            user = db.query(Admin).filter(Admin.id == user_id).first()
        else:
            user = db.query(User).filter(User.id == user_id).first()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        return user

    return role_checker
