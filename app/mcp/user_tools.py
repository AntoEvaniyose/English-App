from app.mcp.server import mcp
from app.db.session import SessionLocal
from app.db.models.user import User


@mcp.tool()
def get_users():

    db = SessionLocal()

    try:

        users = db.query(User).filter(
            User.is_deleted == False
        ).all()

        return [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_active": user.is_active
            }
            for user in users
        ]

    finally:
        db.close()


@mcp.tool()
def get_user(user_id: int):

    db = SessionLocal()

    try:

        user = db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()

        if not user:
            return {"error": "User not found"}

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
            "image": user.image
        }

    finally:
        db.close()