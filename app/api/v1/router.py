from fastapi import APIRouter

from app.api.v1.endpoints import user, health,admin,auth_routes
from app.api.v1.endpoints.admin import package, admin_profile, users
from app.api.v1.endpoints.user import user_content, user_profile, chat

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
api_router.include_router(package.router)
api_router.include_router(user_content.router)
api_router.include_router(admin_profile.router)
api_router.include_router(user_profile.router)
api_router.include_router(users.router)
api_router.include_router(chat.router)
