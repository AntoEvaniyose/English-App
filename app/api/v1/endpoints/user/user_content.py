from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.middleware.role_guard import require_user

import app.services.user.user_content_service as service

router = APIRouter(
    prefix="/user/content",
    tags=["User → Content"],
    dependencies=[Depends(require_user)]
)


@router.get("/packages")
def get_packages(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    return service.get_packages(
        db=db,
        request=request,
        page=page,
        page_size=page_size,
        search=search,
        level=None,
        learning_goal=None,
        current_user=current_user
    )


@router.get("/packages/{package_id}")
def get_package_detail(
    package_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    return service.get_package_detail(
        db=db,
        package_id=package_id,
        current_user=current_user
    )