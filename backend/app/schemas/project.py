"""
Project schemas
"""
from typing import Optional, List, Dict
from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampSchema


class ProjectBase(BaseSchema):
    """Base project fields"""
    slug: str = Field(max_length=100, pattern=r"^[a-z0-9-]+$")
    name: str = Field(max_length=255)
    description: Optional[str] = None
    repository_url: Optional[str] = None
    html_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Project creation schema"""
    team_id: str
    tech_stack: Optional[List[str]] = None
    visibility: str = Field(default="private", pattern=r"^(private|team|public)$")


class ProjectUpdate(BaseSchema):
    """Project update schema"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    repository_url: Optional[str] = None
    html_url: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    visibility: Optional[str] = Field(None, pattern=r"^(private|team|public)$")


class ProjectResponse(ProjectBase, TimestampSchema):
    """Project response schema"""
    id: str
    team_id: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    total_commits: int = 0
    last_synced_at: Optional[datetime] = None
    visibility: str


class ProjectWithStats(ProjectResponse):
    """Project with statistics"""
    type_stats: Dict[str, int] = {}
    recent_commits: List["CommitSummary"] = []


class CommitSummary(BaseSchema):
    """Brief commit info for project response"""
    id: int
    title: str
    type: str
    date: datetime
    author_name: Optional[str] = None


# Update forward references
ProjectWithStats.model_rebuild()
