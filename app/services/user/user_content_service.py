from typing import Optional
from uuid import UUID

from fastapi import Request
from sqlalchemy.orm import Session
from sqlalchemy import case

from app.db.models.content import Package
from app.core.responses import CustomResponse
from app.utils.pagination import paginate_queryset
from app.utils.decorators import try_catch_wrapper


# =====================================
# PACKAGE LIST
# =====================================
@try_catch_wrapper()
def get_packages(
    db: Session,
    request: Request,
    page: int,
    page_size: int,
    search: Optional[str],
    level: Optional[str],
    learning_goal: Optional[str],
    current_user
):

    query = db.query(Package).filter(
        Package.is_active == True
    )

    # =========================
    # SEARCH
    # =========================
    if search:

        search = search.strip()

        query = query.filter(
            Package.title.ilike(f"%{search}%")
        ).order_by(
            case(
                (
                    Package.title.ilike(search),
                    0
                ),
                (
                    Package.title.ilike(f"{search}%"),
                    1
                ),
                (
                    Package.title.ilike(f"%{search}%"),
                    2
                ),
                else_=3
            ),
            Package.title
        )

    else:

        query = query.order_by(
            Package.created_at.desc()
        )

    # =========================
    # PAGINATION
    # =========================
    paginated = paginate_queryset(
        query,
        page,
        page_size,
        request
    )

    return CustomResponse.success(
        "Packages fetched",
        {
            **paginated,
            "results": [
                {
                    "id": package.id,
                    "title": package.title,
                    "description": package.description,
                    "estimated_time": package.estimated_time,
                    "is_active": package.is_active,
                    "created_at": package.created_at
                }
                for package in paginated["results"]
            ]
        }
    )


# =====================================
# PACKAGE DETAIL
# =====================================
@try_catch_wrapper()
def get_package_detail(
    db: Session,
    package_id: UUID,
    current_user
):

    package = db.query(Package).filter(
        Package.id == package_id,
        Package.is_active == True
    ).first()

    if not package:
        return CustomResponse.not_found(
            "Package not found"
        )

    return CustomResponse.success(
        "Package detail fetched",
        {
            "id": package.id,
            "title": package.title,
            "description": package.description,
            "estimated_time": package.estimated_time,
            "is_active": package.is_active,
            "created_at": package.created_at
        }
    )