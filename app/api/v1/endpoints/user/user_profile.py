from fastapi import (
    APIRouter,
    Depends,
    Form,
    File,
    UploadFile
)
from typing import Optional
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.role_guard import require_user
from app.db.models.user import Gender

import app.services.user.user_profile_service as service

router = APIRouter(
    prefix="/user/profile",
    tags=["User → Profile"],
    dependencies=[Depends(require_user)]
)


@router.get("")
def get_profile(
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    return service.get_user_profile(
        db=db,
        user_id=current_user.id
    )


@router.patch("")
def update_profile(
    name: Optional[str] = Form(None),
    dob: Optional[str] = Form(None),
    gender: Optional[Gender] = Form(None),
    image: Optional[UploadFile] = File(None),

    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):

    return service.update_user_profile(
        db=db,
        user_id=current_user.id,
        name=name,
        dob=dob,
        gender=gender,
        image=image
    )