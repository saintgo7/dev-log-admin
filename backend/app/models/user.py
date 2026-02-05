"""
User model
"""
from typing import Optional, List, TYPE_CHECKING
from enum import Enum

from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.team import TeamMember


class UserRole(str, Enum):
    """User global roles"""
    ADMIN = "admin"
    MEMBER = "member"


class AuthProvider(str, Enum):
    """Authentication providers"""
    LOCAL = "local"
    GITHUB = "github"
    GOOGLE = "google"


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User account model"""

    __tablename__ = "users"

    # Basic info
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Authentication
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    auth_provider: Mapped[str] = mapped_column(
        String(20),
        default=AuthProvider.LOCAL.value,
        nullable=False
    )
    provider_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Role (global)
    role: Mapped[str] = mapped_column(
        String(20),
        default=UserRole.MEMBER.value,
        nullable=False
    )

    # Profile
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    github_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    team_memberships: Mapped[List["TeamMember"]] = relationship(
        "TeamMember",
        back_populates="user",
        foreign_keys="[TeamMember.user_id]",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN.value
