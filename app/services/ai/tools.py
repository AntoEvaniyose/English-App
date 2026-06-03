from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.models.content import Package

from app.core.logger import get_logger

logger = get_logger(__name__)

def get_user_profile(
    db: Session,
    user_id: int
):
    
    logger.info(
        f"[TOOL_CALL] get_user_profile user_id={user_id}"
    )

    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()

    if not user:

        logger.warning(
            f"[TOOL_RESULT] user_id={user_id} NOT FOUND"
        )

        return None


    result = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "gender": (
            user.gender.value
            if user.gender else None
        )
    }

    logger.info(
        f"[TOOL_RESULT] get_user_profile={result}"
    )

    return result


def get_packages(
    db: Session
):
    logger.info(
        "[TOOL_CALL] get_packages"
    )

    packages = db.query(Package).filter(
        Package.is_active == True
    ).all()

    logger.info(
        f"[TOOL_RESULT] found {len(packages)} packages"
    )

    return [
        {
            "id": str(package.id),
            "title": package.title,
            "description": package.description,
            "estimated_time": package.estimated_time
        }
        for package in packages
    ]