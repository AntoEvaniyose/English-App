from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.middleware.role_guard import require_admin
from uuid import UUID

import app.services.admin.user_service as service

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin → Users"],
    dependencies=[Depends(require_admin)]
)


# =========================
# LIST USERS
# =========================
@router.get("")
def get_users(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_email_verified: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    return service.get_users(
        db,
        request,
        page,
        page_size,
        search,
        is_active,
        is_email_verified
    )

# =========================
# USER DETAIL
# =========================
@router.get("/{user_id}")
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db)
):
    return service.get_user_detail(db, user_id)

# =========================
# BLOCK / UNBLOCK USER
# =========================
@router.patch("/{user_id}/status")
def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db)
):
    return service.toggle_user_status(db, user_id)
