from pydantic import BaseModel, Field, ValidationInfo, field_validator
from typing import Optional
from datetime import datetime

from app.db.models.user import UserRole


class AdminProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole

    is_active: bool

    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]

class AdminProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=120)
    email: Optional[str] = None

class AdminChangePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info: ValidationInfo):
        if info.data.get("new_password") != v:
            raise ValueError("Passwords do not match")
        return v