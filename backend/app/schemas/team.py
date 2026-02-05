"""
Team schemas
"""
from typing import Optional, List

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampSchema


class TeamBase(BaseSchema):
    """Base team fields"""
    name: str = Field(max_length=255)
    slug: str = Field(max_length=100, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = None
    avatar_url: Optional[str] = None


class TeamCreate(TeamBase):
    """Team creation schema"""
    pass


class TeamUpdate(BaseSchema):
    """Team update schema"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    avatar_url: Optional[str] = None


class TeamResponse(TeamBase, TimestampSchema):
    """Team response schema"""
    id: str
    plan: str


class TeamWithMembers(TeamResponse):
    """Team with members"""
    members: List["TeamMemberResponse"] = []
    member_count: int = 0


class TeamMemberCreate(BaseSchema):
    """Team member creation schema"""
    email: str  # Email of user to invite
    role: str = Field(default="member", pattern=r"^(admin|member|viewer)$")


class TeamMemberUpdate(BaseSchema):
    """Team member update schema"""
    role: str = Field(pattern=r"^(admin|member|viewer)$")


class TeamMemberResponse(TimestampSchema):
    """Team member response schema"""
    user_id: str
    team_id: str
    role: str
    is_active: bool

    # User info (when joined)
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    user_avatar_url: Optional[str] = None


class TeamInvitation(BaseSchema):
    """Team invitation schema"""
    team_id: str
    team_name: str
    team_slug: str
    invited_by_name: Optional[str] = None
    role: str


# Update forward references
TeamWithMembers.model_rebuild()
