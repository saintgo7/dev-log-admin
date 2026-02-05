"""
User service
"""
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


class UserError(Exception):
    """User operation error"""
    pass


class UserService:
    """Service for user operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def list_users(
        self,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None
    ) -> tuple[List[User], int]:
        """
        List users with pagination

        Args:
            limit: Max results
            offset: Skip count
            search: Search term for email/name

        Returns:
            Tuple of (users, total_count)
        """
        query = select(User)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                User.email.ilike(search_term) | User.name.ilike(search_term)
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar() or 0

        # Get results
        query = query.order_by(User.created_at.desc())
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        users = list(result.scalars().all())

        return users, total_count

    async def update_user(
        self,
        user: User,
        data: UserUpdate
    ) -> User:
        """
        Update user profile

        Args:
            user: User to update
            data: Update data

        Returns:
            Updated user
        """
        if data.name is not None:
            user.name = data.name
        if data.avatar_url is not None:
            user.avatar_url = data.avatar_url
        if data.bio is not None:
            user.bio = data.bio
        if data.github_username is not None:
            user.github_username = data.github_username

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def deactivate_user(self, user: User) -> None:
        """
        Deactivate user account

        Args:
            user: User to deactivate
        """
        user.is_active = False
        await self.db.flush()

    async def activate_user(self, user: User) -> None:
        """
        Activate user account

        Args:
            user: User to activate
        """
        user.is_active = True
        await self.db.flush()

    async def verify_user(self, user: User) -> None:
        """
        Mark user as verified

        Args:
            user: User to verify
        """
        user.is_verified = True
        await self.db.flush()


# Import for list_users - placed here to avoid import at module level
from sqlalchemy import func
