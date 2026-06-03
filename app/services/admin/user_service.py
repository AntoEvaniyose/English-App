from typing import Optional

from fastapi import Request
from sqlalchemy import case, or_
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.core.responses import CustomResponse
from app.utils.pagination import paginate_queryset
from app.utils.decorators import try_catch_wrapper


# =====================================
# GET USERS
# =====================================
@try_catch_wrapper()
def get_users(
    db: Session,
    request: Request,
    page: int,
    page_size: int,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_email_verified: Optional[bool] = None
):

    query = db.query(User).filter(
        User.is_deleted == False
    )

    # =========================
    # SEARCH
    # =========================
    if search:

        search = search.strip()

        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        ).order_by(
            case(
                (User.name.ilike(search), 0),
                (User.name.ilike(f"{search}%"), 1),
                (User.email.ilike(f"{search}%"), 2),
                else_=3
            ),
            User.created_at.desc()
        )

    else:

        query = query.order_by(
            User.created_at.desc()
        )

    # =========================
    # FILTERS
    # =========================
    if is_active is not None:
        query = query.filter(
            User.is_active == is_active
        )

    if is_email_verified is not None:
        query = query.filter(
            User.is_email_verified == is_email_verified
        )

    # =========================
    # PAGINATION
    # =========================
    paginated_data = paginate_queryset(
        query,
        page,
        page_size,
        request
    )

    paginated_data["results"] = [
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

            "last_login_at": user.last_login_at,
            "created_at": user.created_at
        }
        for user in paginated_data["results"]
    ]

    return CustomResponse.success(
        "Users fetched successfully",
        paginated_data
    )


# =====================================
# GET USER DETAIL
# =====================================
@try_catch_wrapper()
def get_user_detail(
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
        "User fetched successfully",
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

            "token_version": user.token_version,

            "last_login_at": user.last_login_at,
            "created_at": user.created_at,
            "updated_at": user.updated_at,

            "password_changed_at": user.password_changed_at,

            "is_deleted": user.is_deleted,
            "deleted_at": user.deleted_at
        }
    )


# =====================================
# BLOCK / UNBLOCK USER
# =====================================
@try_catch_wrapper()
def toggle_user_status(
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

    user.is_active = not user.is_active

    db.commit()
    db.refresh(user)

    return CustomResponse.success(
        (
            "User activated successfully"
            if user.is_active
            else "User blocked successfully"
        ),
        {
            "user_id": user.id,
            "is_active": user.is_active
        }
    )