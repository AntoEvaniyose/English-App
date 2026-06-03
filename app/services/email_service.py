# app/services/email_service.py

import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

def send_otp_email(to_email: str, otp: str):
    msg = MIMEText(f"Your login OTP is: {otp}")
    msg["Subject"] = "Login OTP"
    msg["From"] = settings.EMAIL_USER
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
        server.send_message(msg)

def send_password_reset_email(to_email: str, reset_link: str):
    msg = MIMEText(f"Click here to reset your password:\n{reset_link}")
    msg["Subject"] = "Password Reset"
    msg["From"] = settings.EMAIL_USER
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
        server.send_message(msg)