from celery import shared_task
from app.services.email_service import send_otp_email, send_password_reset_email


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 3})
def send_user_otp(self, to_email: str, otp: str):
    send_otp_email(to_email, otp)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 3})
def send_admin_otp(self, to_email: str, otp: str):
    send_otp_email(to_email, otp)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 3})
def send_reset_email(self, to_email: str, reset_link: str):
    send_password_reset_email(to_email, reset_link)