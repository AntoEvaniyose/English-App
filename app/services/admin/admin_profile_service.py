from sqlalchemy.orm import Session
from app.utils.decorators import try_catch_wrapper

from app.db.models.admin import Admin
from app.core.responses import CustomResponse
from app.core.security import verify_password, hash_password


# =========================
# GET ADMIN PROFILE
# =========================
@try_catch_wrapper()
def get_admin_profile(db: Session, admin_id: int):

    admin = db.query(Admin).filter(
        Admin.id == admin_id,
        Admin.is_active == True
    ).first()

    if not admin:
        return CustomResponse.not_found("Admin not found")

    return CustomResponse.success(
        "Admin profile fetched",
        {
            "id": admin.id,
            "name": admin.name,
            "email": admin.email,
            "role": admin.role,

            "is_active": admin.is_active,

            "created_at": admin.created_at,
            "updated_at": admin.updated_at,
            "last_login_at": admin.last_login_at
        }
    )

@try_catch_wrapper()
def update_admin_profile(db: Session, admin_id: int, payload):

    admin = db.query(Admin).filter(
        Admin.id == admin_id,
        Admin.is_active == True
    ).first()

    if not admin:
        return CustomResponse.not_found("Admin not found")

    data = payload.model_dump(exclude_unset=True)

    if not data:
        return CustomResponse.bad_request("No fields provided")

    # optional email uniqueness check
    if "email" in data:
        existing = db.query(Admin).filter(
            Admin.email == data["email"],
            Admin.id != admin_id
        ).first()
        if existing:
            return CustomResponse.bad_request("Email already in use")

    for key, value in data.items():
        setattr(admin, key, value)

    db.commit()
    db.refresh(admin)

    return CustomResponse.success("Profile updated successfully", admin)

@try_catch_wrapper()
def change_admin_password(db: Session, admin_id: int, payload):

    admin = db.query(Admin).filter(
        Admin.id == admin_id,
        Admin.is_active == True
    ).first()

    if not admin:
        return CustomResponse.not_found("Admin not found")

    # 🔐 verify old password
    if not verify_password(payload.old_password, admin.hashed_password):
        return CustomResponse.bad_request("Old password is incorrect")

    # 🔐 hash new password
    admin.hashed_password = hash_password(payload.new_password)

    db.commit()

    return CustomResponse.success("Password updated successfully")