from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.role_guard import get_current_admin

from app.schemas.admin.admin_profile import AdminProfileUpdate, AdminChangePassword
import app.services.admin.admin_profile_service as service

router = APIRouter(
    prefix="/admin/profile",
    tags=["Admin → Profile"],
    dependencies=[Depends(get_current_admin)]
)


# =========================
# GET MY PROFILE
# =========================
@router.get("")
def get_profile(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    return service.get_admin_profile(
        db,
        admin_id=current_admin.id
    )

@router.patch("")
def update_profile(
    payload: AdminProfileUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    return service.update_admin_profile(
        db,
        admin_id=current_admin.id,
        payload=payload
    )


# =========================
# CHANGE PASSWORD
# =========================
@router.post("/change-password")
def change_password(
    payload: AdminChangePassword,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    return service.change_admin_password(
        db,
        admin_id=current_admin.id,
        payload=payload
    )