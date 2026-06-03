from sqlalchemy.orm import Session
from datetime import datetime

from fastapi import UploadFile

from app.db.models.user import User, Gender
from app.core.responses import CustomResponse
from app.utils.file_utils import (
    save_user_profile,
    delete_file
)
from app.utils.decorators import try_catch_wrapper


@try_catch_wrapper()
def get_user_profile(
    db: Session,
    user_id: int
):

    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()

    if not user:
        return CustomResponse.not_found(
            "User not found"
        )

    return CustomResponse.success(
        "User profile fetched",
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,

            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,

            "dob": (
                user.dob.strftime("%d-%m-%Y")
                if user.dob else None
            ),

            "gender": user.gender,
            "image": user.image,

            "created_at": user.created_at,
            "last_login_at": user.last_login_at,
        }
    )


@try_catch_wrapper()
def update_user_profile(
    db: Session,
    user_id: int,
    name: str = None,
    dob: str = None,
    gender: Gender = None,
    image: UploadFile = None
):

    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,
        User.is_active == True
    ).first()

    if not user:
        return CustomResponse.not_found(
            "User not found"
        )

    updated = False

    # =========================
    # NAME
    # =========================
    if name is not None:

        name = name.strip()

        if len(name) < 3:
            return CustomResponse.bad_request(
                "Name must be at least 3 characters"
            )

        user.name = name
        updated = True

    # =========================
    # DOB
    # =========================
    if dob:

        try:
            user.dob = datetime.strptime(
                dob,
                "%d-%m-%Y"
            ).date()

            updated = True

        except ValueError:
            return CustomResponse.bad_request(
                "DOB must be in format DD-MM-YYYY"
            )

    # =========================
    # GENDER
    # =========================
    if gender:

        user.gender = gender
        updated = True

    # =========================
    # PROFILE IMAGE
    # =========================
    if image:

        if user.image:
            delete_file(user.image)

        user.image = save_user_profile(
            image
        )

        updated = True

    if not updated:
        return CustomResponse.bad_request(
            "No fields provided"
        )

    db.commit()
    db.refresh(user)

    return CustomResponse.success(
        "Profile updated successfully",
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,

            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,

            "dob": (
                user.dob.strftime("%d-%m-%Y")
                if user.dob else None
            ),

            "gender": user.gender,
            "image": user.image,

            "created_at": user.created_at,
            "last_login_at": user.last_login_at,
        }
    )