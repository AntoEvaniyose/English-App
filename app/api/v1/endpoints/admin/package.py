from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.middleware.role_guard import require_admin
from typing import Optional
from app.schemas.admin.package import PackageCreate, PackageUpdate
import app.services.admin.package_service as service

router = APIRouter(
    prefix="/admin/packages",
    tags=["Admin → Packages"],
    dependencies=[Depends(require_admin)]
)

# =========================
# CREATE
# =========================
@router.post("")
def create_package(payload: PackageCreate, db: Session = Depends(get_db)):
    return service.create_package(db, payload)


# =========================
# GET ALL
# =========================

@router.get("")
def get_packages(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return service.get_packages(db, request, page, page_size, search)


# =========================
# GET ONE
# =========================
@router.get("/{package_id}")
def get_package(package_id: UUID, db: Session = Depends(get_db)):
    return service.get_package(db, package_id)


# =========================
# UPDATE
# =========================
@router.patch("/{package_id}")
def update_package(
    package_id: UUID,
    payload: PackageUpdate,
    db: Session = Depends(get_db)
):
    return service.update_package(db, package_id, payload)


# =========================
# DELETE
# =========================
@router.delete("/{package_id}")
def delete_package(package_id: UUID, db: Session = Depends(get_db)):
    return service.delete_package(db, package_id)