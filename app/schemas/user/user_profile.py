from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime

from app.db.models.user import UserRole, Gender


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole

    is_active: bool
    is_email_verified: bool

    dob: Optional[str] = None
    gender: Optional[Gender] = None

    streak_count: int
    xp_points: int

    created_at: datetime
    last_login_at: Optional[datetime]

class UserProfileUpdate(BaseModel):

    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=120
    )

    dob: Optional[date] = None

    gender: Optional[Gender] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):

        if v is not None and not v.strip():
            raise ValueError(
                "Name cannot be empty"
            )

        return v.strip()

    @field_validator("dob", mode="before")
    @classmethod
    def validate_dob(cls, v):

        if v is None:
            return None

        if isinstance(v, str):

            if not v.strip():
                return None

            try:
                return datetime.strptime(
                    v,
                    "%d-%m-%Y"
                ).date()

            except ValueError:
                raise ValueError(
                    "DOB must be in format DD-MM-YYYY"
                )

        return v