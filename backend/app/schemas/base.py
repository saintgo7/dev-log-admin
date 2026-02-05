"""
Base schema configurations
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PaginationParams(BaseSchema):
    """Pagination parameters"""
    limit: int = 50
    offset: int = 0

    def __init__(self, limit: int = 50, offset: int = 0, **kwargs):
        super().__init__(limit=min(limit, 100), offset=offset, **kwargs)


class PaginatedResponse(BaseSchema):
    """Paginated response wrapper"""
    total: int
    limit: int
    offset: int
