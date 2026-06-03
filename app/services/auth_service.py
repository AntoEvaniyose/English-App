from datetime import datetime, timedelta, timezone
import hashlib
import random
import base64
from sqlalchemy.orm import Session

from app.core.responses import CustomResponse
from app.db.models.admin import Admin

from app.core.security import (
    hash_password,
    logout,
    # refresh_access_token_user,
    verify_password,
    generate_login_tokens,
    create_password_reset_token,
    verify_password_reset_token,
)
from datetime import datetime, timezone, timedelta

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_token
)

from app.db.models.user import User, UserRole, UserRefreshToken
from app.utils import try_catch_wrapper
from app.utils.otp import generate_otp, verify_otp
from app.utils.login_attempts import is_blocked, increment_attempts, reset_attempts, MAX_ATTEMPTS
from app.utils.ip_utils import get_client_ip
from tasks.email_tasks import send_admin_otp, send_user_otp, send_reset_email

# =======================
# OTP STORE (TEMP)
# =======================
# ⚠️ Replace with Redis in production and expiry
#  store only hash in Redis and compare hash of incoming OTP for better security
# "otp": hashlib.sha256(otp.encode()).hexdigest(),  # 🔥 hashed
#         "expires": now + timedelta(minutes=OTP_EXPIRY_MINUTES),
#         "attempts": 0,
#         "last_sent": now
  
# =======================
# REGISTER ADMIN
# =======================
@try_catch_wrapper("Admin Registration failed,Please try after some time")
def register_admin(db: Session, name: str, email: str, password: str):

    existing = db.query(Admin).filter(Admin.email == email).first()
    if existing:
        return CustomResponse.forbidden("Admin already exists")

    admin = Admin(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        role=UserRole.ADMIN,
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return CustomResponse.success("Admin registered successfully")


# =======================
# LOGIN STEP 1 (PASSWORD → OTP)
# =======================
@try_catch_wrapper()
def login_admin_request_otp(db, email, password, request):

    ip = get_client_ip(request)

    # 🚫 BLOCK CHECK
    blocked, msg = is_blocked(ip)
    if blocked:
        return CustomResponse.forbidden(msg)

    admin = db.query(Admin).filter(Admin.email == email).first()

    if not admin or not verify_password(password, admin.hashed_password):
        attempts = increment_attempts(ip)
        remaining = MAX_ATTEMPTS - attempts

        return CustomResponse.bad_request(
            f"Invalid credentials. {max(remaining, 0)} attempts remaining."
        )

    # ✅ SUCCESS
    reset_attempts(ip)

    otp = generate_otp(email)
    send_admin_otp.delay(email, otp)

    return CustomResponse.success("OTP sent successfully")


# =======================
# LOGIN STEP 2 (VERIFY OTP)
# =======================
@try_catch_wrapper()
def login_admin_verify_otp(db, email, otp):

    if not verify_otp(email, otp):
        return CustomResponse.bad_request("Invalid or expired OTP")

    admin = db.query(Admin).filter(Admin.email == email).first()

    tokens = generate_login_tokens(admin, db, "admin", True)

    return CustomResponse.success("Login successful", tokens)


# =======================
# RESEND OTP
# =======================
@try_catch_wrapper()
def resend_admin_otp(email):
    otp = generate_otp(email)
    send_admin_otp.delay(email, otp)

    return CustomResponse.success("OTP resent")

# =======================
# FORGOT PASSWORD
# =======================
@try_catch_wrapper("Admin forgot password failed,Please try after some time")
def admin_forgot_password(db, email):

    admin = db.query(Admin).filter(
        Admin.email == email,
        Admin.is_active == True
    ).first()

    if not admin:
        return CustomResponse.bad_request("Admin not found")

    if admin.password_changed_at is None:
        admin.password_changed_at = datetime.now(timezone.utc)
        db.commit()

    uid = base64.urlsafe_b64encode(str(admin.id).encode()).decode()
    token = create_password_reset_token(admin)

    link = f"http://localhost:3000/admin/reset-password?uid={uid}&token={token}"

    send_reset_email.delay(email, link)

    return CustomResponse.success("Reset link sent")

@try_catch_wrapper("Admin reset password failed,Please try after some time")
def admin_reset_password(db: Session, data):

    if data.new_password != data.confirm_password:
        return CustomResponse.bad_request("Passwords do not match")

    email, pwd_ts = verify_password_reset_token(data.token)

    if not email or not pwd_ts:
        return CustomResponse.bad_request("Invalid or expired token")

    try:
        user_id = int(base64.urlsafe_b64decode(data.uid.encode()).decode())
    except:
        return CustomResponse.bad_request("Invalid reset link")

    admin = db.query(Admin).filter(
        Admin.id == user_id,
        Admin.email == email
    ).first()

    if not admin:
        return CustomResponse.bad_request("Invalid reset link")

    # =========================
    # STEP 4: TOKEN VALIDATION
    # =========================
    if admin.password_changed_at and int(admin.password_changed_at.timestamp()) != pwd_ts:
        return CustomResponse.bad_request("Link already used")

    # =========================
    # STEP 5: UPDATE PASSWORD
    # =========================
    admin.hashed_password = hash_password(data.new_password)
    admin.password_changed_at = datetime.now(timezone.utc)

    db.commit()

    return CustomResponse.success("Password reset successful")


# =======================
# USER
# =======================

# ============================================
# RESEND USER OTP LOGIN
# ============================================

@try_catch_wrapper("Failed to resend OTP")
def resend_otp_user_register(
    db: Session,
    email: str
):

    email = email.strip().lower()

    # =========================
    # CHECK USER
    # =========================
    user = db.query(User).filter(
        User.email == email,
        User.is_deleted == False
    ).first()

    if not user:
        return CustomResponse.bad_request(
            "User not found"
        )

    # =========================
    # BLOCK VERIFIED USERS
    # =========================
    if user.is_active and user.is_email_verified:
        return CustomResponse.bad_request(
            "User already verified. Please login."
        )

    # =========================
    # GENERATE NEW OTP
    # =========================
    otp = generate_otp(email)

    # =========================
    # SEND OTP
    # =========================
    send_user_otp.delay(email, otp)

    return CustomResponse.success(
        "OTP resent successfully"
    )


# =======================
# RESEND OTP
# =======================
@try_catch_wrapper()
def resend_otp_user(db: Session, email: str):

    email = email.strip().lower()

    # =========================
    # CHECK USER
    # =========================
    user = db.query(User).filter(
        User.email == email,
        User.is_deleted == False
    ).first()

    if not user:
        return CustomResponse.bad_request("User not found")

    # =========================
    # BLOCK IF ALREADY VERIFIED
    # =========================
    # if user.is_active and user.is_email_verified:
    #     return CustomResponse.bad_request("User already verified. Please login.")

    # =========================
    # ONLY ALLOW IF NOT VERIFIED
    # =========================
    if user.is_active and user.is_email_verified:
        otp = generate_otp(email)

        # async email
        send_user_otp.delay(email, otp)

        return CustomResponse.success("OTP resent successfully")

    # fallback (rare case)
    return CustomResponse.bad_request("Unable to resend OTP")

# =======================
# VERIFY OTP REGISTER
# =======================
@try_catch_wrapper("User Registration failed, Please try after some time")
def register_user(db: Session, name: str, email: str, password: str):

    email = email.strip().lower()
    name = name.strip()

    existing = db.query(User).filter(User.email == email).first()

    # =========================
    # USER EXISTS
    # =========================
    if existing:

        # Already verified → block
        if existing.is_email_verified:
            return CustomResponse.bad_request("User already exists")

        # Not verified → update + resend OTP
        existing.name = name
        existing.hashed_password = hash_password(password)
        existing.is_active = False

        db.commit()
        db.refresh(existing)

        otp = generate_otp(email)
        send_user_otp.delay(email, otp)

        return CustomResponse.success(
            "OTP resent. Please verify your email."
        )

    # =========================
    # NEW USER
    # =========================
    user = User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        role=UserRole.USER,
        is_active=False,
        is_email_verified=False,
        created_at=datetime.now(timezone.utc)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    otp = generate_otp(email)
    send_user_otp.delay(email, otp)

    return CustomResponse.success(
        "User registered successfully. Please verify your email."
    )

# ============================================
# VERIFY REGISTER OTP
# ============================================
@try_catch_wrapper("OTP verification failed, Please try again")
def verify_register_otp(
    db: Session,
    email: str,
    otp: str
):

    email = email.strip().lower()

    # =========================
    # VERIFY OTP (REDIS)
    # =========================
    if not verify_otp(email, str(otp)):
        return CustomResponse.bad_request(
            "Invalid or expired OTP"
        )

    # =========================
    # GET USER
    # =========================
    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        return CustomResponse.not_found(
            "User not found"
        )

    # =========================
    # ACTIVATE USER
    # =========================
    user.is_active = True
    user.is_email_verified = True
    user.last_login_at = datetime.now(timezone.utc)

    # =========================
    # CREATE TOKENS
    # =========================
    access_token = create_access_token({
        "sub": str(user.id),
        "id": user.id,
        "role": user.role.value,
        "token_version": user.token_version
    })

    refresh_token = create_refresh_token({
        "sub": str(user.id),
        "id": user.id,
        "role": user.role.value,
        "token_version": user.token_version
    })

    # =========================
    # STORE REFRESH TOKEN
    # =========================
    refresh_entry = UserRefreshToken(
        user_id=user.id,
        token=hash_token(refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(
            days=30
        )
    )

    db.add(refresh_entry)

    db.commit()
    db.refresh(user)

    # =========================
    # RESPONSE
    # =========================
    return CustomResponse.success(
        "Email verified successfully",
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "role": user.role.value,

            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_active": user.is_active,
                "is_email_verified": user.is_email_verified
            }
        }
    )

# =======================
# LOGIN (EMAIL/PASSWORD)
# =======================
@try_catch_wrapper("User Login failed,Please try after some time")
def login_with_otp(db, email, password, request):

    email = email.strip().lower()

    ip = get_client_ip(request)

    # =====================================================
    # BLOCK CHECK
    # =====================================================

    blocked, msg = is_blocked(ip)

    if blocked:

        return CustomResponse.forbidden(msg)

    # =====================================================
    # USER CHECK
    # =====================================================

    user = db.query(User).filter(
        User.email == email,
        User.is_deleted == False
    ).first()

    if not user or not verify_password(
        password,
        user.hashed_password
    ):

        attempts = increment_attempts(ip)

        remaining = MAX_ATTEMPTS - attempts

        return CustomResponse.bad_request(
            f"Invalid credentials. "
            f"{max(remaining, 0)} attempts remaining."
        )

    # =====================================================
    # USER ACTIVE CHECK
    # =====================================================

    if not user.is_active:

        return CustomResponse.forbidden(
            "User account is blocked"
        )

    # =====================================================
    # EMAIL VERIFIED CHECK
    # =====================================================

    if not user.is_email_verified:

        return CustomResponse.forbidden(
            "Please verify your email first"
        )

    # =====================================================
    # SUCCESS
    # =====================================================

    reset_attempts(ip)

    otp = generate_otp(email)

    send_user_otp.delay(
        email,
        otp
    )

    return CustomResponse.success(
        "OTP sent successfully"
    )

# =======================
# VERIFY OTP LOGIN
# =======================
@try_catch_wrapper()
def verify_login_otp(db, email, otp):

    email = email.strip().lower()

    # =====================================================
    # VERIFY OTP
    # =====================================================

    if not verify_otp(email, otp):

        return CustomResponse.bad_request(
            "Invalid OTP"
        )

    # =====================================================
    # USER
    # =====================================================

    user = db.query(User).filter(
        User.email == email,
        User.is_deleted == False
    ).first()

    if not user:

        return CustomResponse.not_found(
            "User not found"
        )

    # =====================================================
    # USER ACTIVE
    # =====================================================

    if not user.is_active:

        return CustomResponse.forbidden(
            "User account is blocked"
        )

    # =====================================================
    # LAST LOGIN
    # =====================================================

    user.last_login_at = datetime.now(
        timezone.utc
    )

    # =====================================================
    # TOKENS
    # =====================================================

    tokens = generate_login_tokens(
        user,
        db,
        user.role,
        False
    )

    db.commit()

    return CustomResponse.success(
        "Login successful",
        tokens
    )


# =======================
# REFRESH TOKEN USER
# =======================
# @try_catch_wrapper()
# def refresh_user_token(refresh_token: str, db: Session):
#     return refresh_access_token_user(refresh_token, db)


# =======================
# LOGOUT
# =======================
@try_catch_wrapper()
def logout_user(refresh_token: str, db: Session, is_admin: bool = False):
    return logout(refresh_token, db,is_admin=is_admin)

@try_catch_wrapper("User forgot password failed,Please try after some time")
def user_forgot_password(db: Session, email: str):

    email = email.strip().lower()

    user = db.query(User).filter(
        User.email == email,
        User.is_active == True,
        User.is_email_verified == True,
        User.is_deleted == False
    ).first()

    if not user:
        return CustomResponse.bad_request(
            "User not found."
        )

    if user.password_changed_at is None:
        user.password_changed_at = datetime.now(timezone.utc)
        db.commit()

    uid = base64.urlsafe_b64encode(str(user.id).encode()).decode()
    token = create_password_reset_token(user)

    reset_link = f"http://localhost:3000/user/reset-password?uid={uid}&token={token}"

    send_reset_email.delay(user.email, reset_link)

    return CustomResponse.success(
        "If this email exists, a reset link has been sent."
    )

@try_catch_wrapper("User reset password failed,Please try after some time")
def user_reset_password(db: Session, data):

    if data.new_password != data.confirm_password:
        return CustomResponse.bad_request("Passwords do not match")

    email, pwd_ts = verify_password_reset_token(data.token)

    if not email or not pwd_ts:
        return CustomResponse.bad_request("Invalid or expired token")

    try:
        user_id = int(base64.urlsafe_b64decode(data.uid.encode()).decode())
    except:
        return CustomResponse.bad_request("Invalid reset link")

    user = db.query(User).filter(
        User.id == user_id,
        User.email == email
    ).first()

    if not user:
        return CustomResponse.bad_request("Invalid reset link")

    if user.password_changed_at and int(user.password_changed_at.timestamp()) != pwd_ts:
        return CustomResponse.bad_request("Link already used")

    user.hashed_password = hash_password(data.new_password)
    user.password_changed_at = datetime.now(timezone.utc)

    db.commit()

    return CustomResponse.success("Password reset successful")
