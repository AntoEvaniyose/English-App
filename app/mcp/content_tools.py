from app.mcp.server import mcp
from app.db.session import SessionLocal
from app.db.models.content import Package


@mcp.tool()
def get_packages():

    db = SessionLocal()

    try:

        packages = db.query(Package).filter(
            Package.is_active == True
        ).all()

        return [
            {
                "id": str(package.id),
                "title": package.title,
                "description": package.description,
                "estimated_time": package.estimated_time
            }
            for package in packages
        ]

    finally:
        db.close()


@mcp.tool()
def get_package(package_id: str):

    db = SessionLocal()

    try:

        package = db.query(Package).filter(
            Package.id == package_id
        ).first()

        if not package:
            return {"error": "Package not found"}

        return {
            "id": str(package.id),
            "title": package.title,
            "description": package.description,
            "estimated_time": package.estimated_time
        }

    finally:
        db.close()