"""
Commit schemas
"""
from typing import Optional
from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampSchema, PaginatedResponse


class CommitBase(BaseSchema):
    """Base commit fields"""
    type: str = Field(max_length=50)
    title: str = Field(max_length=500)
    author_name: Optional[str] = Field(None, max_length=255)
    author_email: Optional[str] = Field(None, max_length=255)
    date: datetime


class CommitCreate(CommitBase):
    """Commit creation schema"""
    project_id: str
    log_number: Optional[int] = None
    commit_hash: Optional[str] = Field(None, max_length=40)
    files_changed: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    full_content: Optional[str] = None


class CommitUpdate(BaseSchema):
    """Commit update schema"""
    type: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = Field(None, max_length=500)
    full_content: Optional[str] = None


class CommitResponse(CommitBase, TimestampSchema):
    """Commit response schema"""
    id: int
    project_id: str
    log_number: Optional[int] = None
    commit_hash: Optional[str] = None
    files_changed: int = 0
    lines_added: int = 0
    lines_deleted: int = 0


class CommitDetail(CommitResponse):
    """Full commit detail with content"""
    full_content: Optional[str] = None
    project_slug: Optional[str] = None
    project_name: Optional[str] = None


class CommitListResponse(PaginatedResponse):
    """Paginated commit list response"""
    commits: list[CommitResponse] = []


class CommitSearchResult(CommitResponse):
    """Commit search result with project info"""
    project_slug: str
    project_name: str
