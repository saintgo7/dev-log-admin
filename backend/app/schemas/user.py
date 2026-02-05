"""
User schemas
"""
from typing import Optional, List

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema, TimestampSchema


class UserBase(BaseSchema):
    """Base user fields"""
    email: EmailStr
    name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    github_username: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(min_length=8)


class UserUpdate(BaseSchema):
    """User update schema"""
    name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    github_username: Optional[str] = Field(None, max_length=255)


class UserResponse(UserBase, TimestampSchema):
    """User response schema"""
    id: str
    role: str
    is_active: bool
    is_verified: bool
    auth_provider: str


class UserInDB(UserResponse):
    """User in database (includes hashed password)"""
    hashed_password: Optional[str] = None


class UserWithTeams(UserResponse):
    """User with team memberships"""
    teams: List["TeamMembershipInfo"] = []


class TeamMembershipInfo(BaseSchema):
    """Team membership info for user response"""
    team_id: str
    team_name: str
    team_slug: str
    role: str


# Update forward reference
UserWithTeams.model_rebuild()
