"""
Commit model - unified Phase 2 and Phase 3
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
    """Commit/Dev log entry model - supports both manual logs and GitHub sync"""

    __tablename__ = "commits"

    # Project relationship
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Commit info (supports both manual and GitHub)
    log_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    commit_hash: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)  # Phase 2 field
    sha: Mapped[Optional[str]] = mapped_column(String(40), nullable=True, unique=True)  # Phase 3 field (GitHub)

    type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # Phase 2 field
    commit_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # Phase 3 field

    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Phase 2 field
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Phase 3 field

    # Author info
    author_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Phase 2
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Phase 3
    author_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Date
    date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    commit_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )

    # Stats
    files_changed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lines_added: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Phase 2
    lines_deleted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Phase 2
    insertions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Phase 3
    deletions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Phase 3

    # Content
    full_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Phase 2
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Phase 3 - GitHub URL

    # Relationship
    project: Mapped["Project"] = relationship("Project", back_populates="commits")

    # Indexes
    __table_args__ = (
        Index("idx_commits_project_date", "project_id", "date"),
        Index("idx_commits_project_commit_date", "project_id", "commit_date"),
        Index("idx_commits_date_desc", "date"),
        Index("idx_commits_sha", "sha"),
    )

    def __repr__(self) -> str:
        identifier = self.sha[:7] if self.sha else (self.commit_hash[:7] if self.commit_hash else str(self.id)[:8])
        msg = self.message or self.title or "No message"
        return f"<Commit {identifier}: {msg[:50]}>"
