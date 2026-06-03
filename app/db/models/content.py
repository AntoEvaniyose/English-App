# app/models/content.py
from __future__ import annotations
import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Enum, ForeignKey,
    Integer, String, Text, Float, JSON, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# ─────────────────────────────────────────────
# Content Hierarchy: Package → Module → Lesson
# ─────────────────────────────────────────────

class Package(Base):
    __tablename__ = "packages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str]         = mapped_column(String(200), nullable=False)
    description: Mapped[str | None]     = mapped_column(Text)
    estimated_time: Mapped[int | None]  = mapped_column(Integer)   # minutes
    is_active: Mapped[bool]             = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now())
