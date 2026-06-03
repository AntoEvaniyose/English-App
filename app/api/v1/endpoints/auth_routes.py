from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db

import app.services.auth_service as auth_service

from app.core.security import refresh_access_token_admin, refresh_user_token


import app.schemas as schemas


router = APIRouter()


# =======================
# REGISTER
# =======================
@router.post("/admin/register")
def register(
    payload :schemas.AdminCreate,
    db: Session = Depends(get_db)
):
   return auth_service.register_admin(db, payload.name, payload.email, payload.password)


# =======================
# LOGIN STEP 1 (PASSWORD → OTP)
# =======================
@router.post("/admin/login/request-otp")
def login_request_otp(
    payload :schemas.AdminLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    return auth_service.login_admin_request_otp(db,payload.email,payload.password, request)


# =======================
# LOGIN STEP 2 (OTP VERIFY)
# =======================
@router.post("/admin/login/verify-otp")
def login_verify_otp(
    payload : schemas.AdminOTP,
    db: Session = Depends(get_db)
):
    return auth_service.login_admin_verify_otp(db,payload.email, 
                                  payload.otp)


# =======================
# RESEND OTP
# =======================
@router.post("/admin/resend-otp")
def resend_otp(payload :schemas.ResendOTPRequest):
    return auth_service.resend_admin_otp(payload.email)


# =======================
# REFRESH TOKEN
# =======================
@router.post("/admin/refresh")
def refresh_token(
    payload : schemas.TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    return refresh_access_token_admin(payload.refresh_token, db)

@router.post("/admin/logout")
def logout_route(data: schemas.TokenRefreshRequest, db: Session = Depends(get_db)):
    return auth_service.logout_user(data.refresh_token, db, is_admin=True)

@router.post("/admin/forgot-password")
def admin_forgot(payload: schemas.AdminForgotPasswordSchema, db: Session = Depends(get_db)):
    return auth_service.admin_forgot_password(db, payload.email)


@router.post("/admin/reset-password")
def admin_reset(payload: schemas.AdminResetPasswordSchema, db: Session = Depends(get_db)):
    return auth_service.admin_reset_password(db, payload)

# =======================
#? REGISTER USER WITH OTP
# =======================
@router.post("/user/register-otp")
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register_user(db, payload.name, payload.email, payload.password)


@router.post("/user/register-verify-otp")
def verify_otp(payload: schemas.UserOTP, db: Session = Depends(get_db)):
    return auth_service.verify_register_otp(db, payload.email, payload.otp)

@router.post("/user/resend-user-register-otp")
def resend_otp(payload :schemas.ResendOTPRequest, db: Session = Depends(get_db)):
    return auth_service.resend_otp_user_register(db, payload.email)

@router.post("/user/resend-user-login-otp")
def resend_otp(payload :schemas.ResendOTPRequest, db: Session = Depends(get_db)):
    return auth_service.resend_otp_user(db, payload.email)

# =======================
# LOGIN
# =======================
@router.post("/user/login-otp")
def login(payload:schemas.UserLoginRequest, request: Request, db: Session = Depends(get_db)):
    return auth_service.login_with_otp(db, payload.email, payload.password, request)


@router.post("/user/login")
def login_verify_otp(payload:schemas.UserOTP, db: Session = Depends(get_db)):
    return auth_service.verify_login_otp(db, payload.email, payload.otp)


# =======================
# REFRESH TOKEN
# =======================
@router.post("/user/refresh")
def refresh(data: schemas.TokenRefreshRequest, db: Session = Depends(get_db)):
    return refresh_user_token(data.refresh_token, db)


# =======================
# LOGOUT
# =======================
@router.post("/user/logout")
def logout_route(data: schemas.TokenRefreshRequest, db: Session = Depends(get_db)):
    return auth_service.logout_user(data.refresh_token, db)

@router.post("/user/forgot-password")
def user_forgot(payload: schemas.UserForgotPasswordSchema, db: Session = Depends(get_db)):
    return auth_service.user_forgot_password(db, payload.email)


@router.post("/user/reset-password")
def user_reset(payload: schemas.UserResetPasswordSchema, db: Session = Depends(get_db)):
    return auth_service.user_reset_password(db, payload)