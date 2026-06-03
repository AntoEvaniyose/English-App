from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy import case
from sqlalchemy.orm import joinedload
from app.db.models.content import Package
from app.db.models.content import Package
from app.core.responses import CustomResponse
from app.utils.pagination import paginate_queryset
from fastapi import Request
from app.utils.decorators import try_catch_wrapper

# =========================
# CREATE PACKAGE
# =========================
@try_catch_wrapper()
def create_package(db: Session, payload):

    existing = db.query(Package).filter(
        Package.title.ilike(payload.title.strip())
    ).first()

    if existing:
        return CustomResponse.bad_request(
            "Package with this title already exists"
        )

    package = Package(
        title=payload.title.strip(),
        description=payload.description,
        estimated_time=payload.estimated_time,
        is_active=payload.is_active
    )

    db.add(package)
    db.commit()
    db.refresh(package)

    return CustomResponse.success(
        "Package created successfully",
        package
    )

# =========================
# GET ALL PACKAGES
# =========================
@try_catch_wrapper()
def get_packages(
    db: Session,
    request: Request,
    page: int,
    page_size: int,
    search=None,
    level=None,
    goal=None
):

    query = db.query(Package)

    # =========================
    # SEARCH
    # =========================
    if search:
        search = search.strip()

        query = query.filter(
            Package.title.ilike(f"%{search}%")
        ).order_by(
            case(
                (Package.title.ilike(search), 0),          # exact
                (Package.title.ilike(f"{search}%"), 1),    # starts with
                (Package.title.ilike(f"%{search}%"), 2),   # contains
                else_=3,
            ),
            Package.title
        )

    else:
        query = query.order_by(Package.created_at.asc())

    # =========================
    # PAGINATION
    # =========================
    paginated_data = paginate_queryset(
        query,
        page,
        page_size,
        request
    )

    return CustomResponse.success(
        "Packages fetched successfully",
        paginated_data
    )

# =========================
# GET SINGLE PACKAGE
# =========================
@try_catch_wrapper()
def get_package(db: Session, package_id: UUID):
    package = db.query(Package).filter(Package.id == package_id).first()

    if not package:
        return CustomResponse.not_found("Package not found")

    return CustomResponse.success("Package fetched successfully", package)


# =========================
# UPDATE PACKAGE
# =========================
@try_catch_wrapper()
def update_package(db: Session, package_id, payload):
    package = db.query(Package).filter(Package.id == package_id).first()

    if not package:
        return CustomResponse.not_found("Package not found")

    update_data = payload.model_dump(exclude_unset=True)

    # ❌ Empty PATCH check
    if not update_data:
        return CustomResponse.bad_request("No fields provided for update")

    # ✅ Unique title check (if updating title)
    if "title" in update_data:
        existing = db.query(Package).filter(
            Package.title == update_data["title"],
            Package.id != package_id
        ).first()

        if existing:
            return CustomResponse.bad_request("Package title already exists")

    # ✅ Apply updates
    for key, value in update_data.items():
        setattr(package, key, value)

    db.commit()
    db.refresh(package)

    return CustomResponse.success("Package updated successfully", package)

# =========================
# DELETE PACKAGE
# =========================
@try_catch_wrapper()
def delete_package(db: Session, package_id: UUID):
    package = db.query(Package).filter(Package.id == package_id).first()

    if not package:
        return CustomResponse.not_found("Package not found")

    db.delete(package)
    db.commit()

    return CustomResponse.success("Package deleted successfully")
