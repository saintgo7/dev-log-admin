"""
Commit model
"""
from typing import Optional, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.project import Project


class Commit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Commit/Dev log entry model"""

    __tablename__ = "commits"

    # Project relationship
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # GitHub commit info
    sha: Mapped[Optional[str]] = mapped_column(String(40), nullable=True, unique=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    commit_type: Mapped[str] = mapped_column(String(50), default="chore", nullable=False, index=True)

    # Author info
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Date
    commit_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # Stats
    files_changed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    insertions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deletions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # URL to GitHub commit
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Legacy fields for v1 compatibility (can be removed later)
    log_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationship
    project: Mapped["Project"] = relationship("Project", back_populates="commits")

    # Indexes
    __table_args__ = (
        Index("idx_commits_project_date", "project_id", "commit_date"),
        Index("idx_commits_sha", "sha"),
    )

    def __repr__(self) -> str:
        return f"<Commit {self.sha[:7] if self.sha else self.id}: {self.message[:50]}>"
