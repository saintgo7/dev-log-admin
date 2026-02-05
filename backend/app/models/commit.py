"""
Commit model
"""
from typing import Optional, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project


class Commit(Base, TimestampMixin):
    """Commit/Dev log entry model"""

    __tablename__ = "commits"

    # Primary key (auto-increment integer for v1 compatibility)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Project relationship
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Commit info
    log_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    commit_hash: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    # Author info
    author_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Date
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # Stats
    files_changed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lines_added: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lines_deleted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Content
    full_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    project: Mapped["Project"] = relationship("Project", back_populates="commits")

    # Indexes
    __table_args__ = (
        Index("idx_commits_project_date", "project_id", "date"),
        Index("idx_commits_date_desc", "date"),
    )

    def __repr__(self) -> str:
        return f"<Commit {self.id}: {self.title[:50]}>"
