from __future__ import annotations
import enum
from datetime import datetime, timezone, date
from sqlalchemy import (
    BigInteger, Boolean, DateTime, Date, Enum, ForeignKey, Index,
    Integer, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from datetime import timedelta

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"

def _utcnow():
    return datetime.now(timezone.utc)

# =========================
# USER MODEL
# =========================
class User(Base):
    __tablename__ = "users"

    # 🔑 Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    # 👤 Identity
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # 🔐 Auth & Security
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER, nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # 👤 Personal Details
    dob: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender), nullable=True)

    token_version: Mapped[int] = mapped_column(Integer, default=0)  # 🔥 global logout

    # 🖼 Profile
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 🧾 Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # 🗑 Soft Delete (important for production apps)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # 🔗 Relationships
    refresh_tokens: Mapped[list["UserRefreshToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # Indexing for performance
    __table_args__ = (
        Index("idx_users_email_active", "email", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"


class UserRefreshToken(Base):
    __tablename__ = "user_refresh_tokens"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    token: Mapped[str] = mapped_column(Text, unique=True, index=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")
