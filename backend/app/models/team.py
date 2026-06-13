"""
Team and TeamMember models
"""
from typing import Optional, List, TYPE_CHECKING
from enum import Enum

from sqlalchemy import String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import GUID, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project


class TeamPlan(str, Enum):
    """Team subscription plans"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class TeamMemberRole(str, Enum):
    """Team member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Team(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Team/Organization model"""

    __tablename__ = "teams"

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Subscription
    plan: Mapped[str] = mapped_column(
        String(20),
        default=TeamPlan.FREE.value,
        nullable=False
    )

    # Settings (JSON stored as text for simplicity)
    settings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    members: Mapped[List["TeamMember"]] = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan"
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="team",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Team {self.slug}>"


class TeamMember(Base, TimestampMixin):
    """Team membership (many-to-many relationship)"""

    __tablename__ = "team_members"

    # Composite primary key
    team_id: Mapped[str] = mapped_column(
        GUID,
        ForeignKey("teams.id", ondelete="CASCADE"),
        primary_key=True
    )
    user_id: Mapped[str] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    # Role within team
    role: Mapped[str] = mapped_column(
        String(20),
        default=TeamMemberRole.MEMBER.value,
        nullable=False
    )

    # Invitation status
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    invited_by: Mapped[Optional[str]] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="team_memberships", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_member"),
    )

    def __repr__(self) -> str:
        return f"<TeamMember team={self.team_id} user={self.user_id}>"

    @property
    def is_owner(self) -> bool:
        """Check if member is team owner"""
        return self.role == TeamMemberRole.OWNER.value

    @property
    def is_admin(self) -> bool:
        """Check if member has admin privileges"""
        return self.role in (TeamMemberRole.OWNER.value, TeamMemberRole.ADMIN.value)

    @property
    def can_write(self) -> bool:
        """Check if member can write"""
        return self.role in (
            TeamMemberRole.OWNER.value,
            TeamMemberRole.ADMIN.value,
            TeamMemberRole.MEMBER.value
        )
