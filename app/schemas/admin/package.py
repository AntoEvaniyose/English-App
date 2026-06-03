from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from typing import Optional


# =========================
# CREATE SCHEMA
# =========================
class PackageCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    estimated_time: Optional[int] = Field(None, gt=0)
    is_active: bool = True

    # Custom validation
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


# =========================
# UPDATE SCHEMA (PATCH)
# =========================
class PackageUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    estimated_time: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v
    

class PackageResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    estimated_time: Optional[int]
    is_active: bool

    class Config:
        from_attributes = True

