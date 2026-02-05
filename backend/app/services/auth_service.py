"""
Authentication service
"""
from datetime import timedelta
from typing import Optional, Tuple
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    TokenExpiredError,
    InvalidTokenError
)
from app.models.user import User, AuthProvider
from app.schemas.auth import Token


class AuthenticationError(Exception):
    """Authentication error"""
    pass


class AuthService:
    """Service for authentication operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(
        self,
        email: str,
        password: str,
        name: Optional[str] = None
    ) -> User:
        """
        Register a new user with email/password

        Args:
            email: User email
            password: Plain text password
            name: Optional display name

        Returns:
            Created user

        Raises:
            AuthenticationError: If email already exists
        """
        # Check if email exists
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        if result.scalar_one_or_none():
            raise AuthenticationError("Email already registered")

        # Create user
        user = User(
            id=str(uuid4()),
            email=email,
            name=name,
            hashed_password=hash_password(password),
            auth_provider=AuthProvider.LOCAL.value,
            is_active=True,
            is_verified=False
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> User:
        """
        Authenticate user with email/password

        Args:
            email: User email
            password: Plain text password

        Returns:
            Authenticated user

        Raises:
            AuthenticationError: If credentials are invalid
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise AuthenticationError("Invalid email or password")

        if user.auth_provider != AuthProvider.LOCAL.value:
            raise AuthenticationError(
                f"This account uses {user.auth_provider} authentication"
            )

        if not user.hashed_password:
            raise AuthenticationError("Password not set for this account")

        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is disabled")

        return user

    async def create_tokens(self, user: User) -> Token:
        """
        Create access and refresh tokens for user

        Args:
            user: Authenticated user

        Returns:
            Token object with access and refresh tokens
        """
        access_token = create_access_token(
            subject=user.id,
            additional_claims={
                "email": user.email,
                "role": user.role
            }
        )
        refresh_token = create_refresh_token(subject=user.id)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRATION_HOURS * 3600
        )

    async def refresh_tokens(self, refresh_token: str) -> Token:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            New token pair

        Raises:
            AuthenticationError: If refresh token is invalid
        """
        try:
            user_id = verify_token(refresh_token, token_type="refresh")
        except (TokenExpiredError, InvalidTokenError) as e:
            raise AuthenticationError(f"Invalid refresh token: {str(e)}")

        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise AuthenticationError("User not found or disabled")

        return await self.create_tokens(user)

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str
    ) -> None:
        """
        Change user password

        Args:
            user: Current user
            current_password: Current password
            new_password: New password

        Raises:
            AuthenticationError: If current password is wrong
        """
        if user.auth_provider != AuthProvider.LOCAL.value:
            raise AuthenticationError(
                "Cannot change password for OAuth accounts"
            )

        if not verify_password(current_password, user.hashed_password):
            raise AuthenticationError("Current password is incorrect")

        user.hashed_password = hash_password(new_password)
        await self.db.flush()

    async def get_or_create_oauth_user(
        self,
        provider: str,
        provider_user_id: str,
        email: str,
        name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> Tuple[User, bool]:
        """
        Get existing user or create new one for OAuth login

        Args:
            provider: OAuth provider (github, google)
            provider_user_id: User ID from provider
            email: User email
            name: Display name
            avatar_url: Avatar URL

        Returns:
            Tuple of (user, is_new)
        """
        # Try to find by provider ID
        result = await self.db.execute(
            select(User).where(
                User.auth_provider == provider,
                User.provider_user_id == provider_user_id
            )
        )
        user = result.scalar_one_or_none()

        if user:
            # Update user info
            user.name = name or user.name
            user.avatar_url = avatar_url or user.avatar_url
            await self.db.flush()
            return user, False

        # Try to find by email
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            # Link OAuth to existing account
            existing_user.auth_provider = provider
            existing_user.provider_user_id = provider_user_id
            existing_user.avatar_url = avatar_url or existing_user.avatar_url
            await self.db.flush()
            return existing_user, False

        # Create new user
        user = User(
            id=str(uuid4()),
            email=email,
            name=name,
            avatar_url=avatar_url,
            auth_provider=provider,
            provider_user_id=provider_user_id,
            is_active=True,
            is_verified=True  # OAuth users are verified
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        return user, True
