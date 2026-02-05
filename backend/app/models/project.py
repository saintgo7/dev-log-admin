"""
Project model
"""
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.commit import Commit


class ProjectVisibility(str, Enum):
    """Project visibility levels"""
    PRIVATE = "private"  # Only team members
    TEAM = "team"        # All teams user belongs to
    PUBLIC = "public"    # Anyone (read-only for non-members)


class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Project model - represents a repository/project"""

    __tablename__ = "projects"

    # Basic info
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Repository info
    repository_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tech_stack: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    html_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Sync info
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    total_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Team relationship
    team_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Visibility
    visibility: Mapped[str] = mapped_column(
        String(20),
        default=ProjectVisibility.PRIVATE.value,
        nullable=False
    )

    # Relationships
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="projects")
    commits: Mapped[List["Commit"]] = relationship(
        "Commit",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project {self.slug}>"

    @property
    def is_public(self) -> bool:
        """Check if project is publicly visible"""
        return self.visibility == ProjectVisibility.PUBLIC.value
