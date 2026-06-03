from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# =====================================================
# IMPORT TASKS
# =====================================================

import tasks.email_tasks

# =====================================================
# CELERY INSTANCE
# =====================================================

celery_app = Celery(

    "english_app",

    broker=settings.CELERY_BROKER_URL,

    backend=settings.CELERY_RESULT_BACKEND,
)


# # =====================================================
# # CELERY CONFIG
# # =====================================================

# celery_app.conf.update(

#     task_serializer="json",

#     accept_content=["json"],

#     result_serializer="json",

#     timezone="UTC",

#     enable_utc=True,

#     beat_schedule={

#         # =============================================
#         # SUBSCRIPTION REMINDER EMAILS
#         # =============================================

#         "subscription-reminder-emails": {

#             "task": (
#                 "tasks.subscription_tasks."
#                 "send_subscription_reminders"
#             ),

#             "schedule": crontab(minute="*/30"),
#         },

#         # =============================================
#         # DEACTIVATE EXPIRED USERS
#         # =============================================

#         "deactivate-expired-users": {

#             "task": (
#                 "tasks.subscription_tasks."
#                 "deactivate_expired_users"
#             ),

#             "schedule": crontab(minute="*/30"),
#         },
#     }
# )


# =====================================================
# AUTO DISCOVER TASKS
# =====================================================

celery_app.autodiscover_tasks([
    "tasks"
])