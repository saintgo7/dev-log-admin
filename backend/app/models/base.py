"""
Base model with common fields
"""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import CHAR, JSON, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

# PostgreSQL 네이티브 타입을 SQLite(테스트)에서도 컴파일되도록 variant로 래핑한다.
# 운영 PostgreSQL에서는 UUID / JSONB 그대로, SQLite에서는 CHAR(36) / JSON 으로 렌더된다.
GUID = UUID(as_uuid=False).with_variant(CHAR(36), "sqlite")
JSONBType = JSONB().with_variant(JSON(), "sqlite")


def utcnow() -> datetime:
    """Return current UTC time"""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False
    )


class UUIDPrimaryKeyMixin:
    """Mixin for UUID primary key"""

    id: Mapped[str] = mapped_column(
        GUID,
        primary_key=True,
        default=lambda: str(uuid4())
    )
