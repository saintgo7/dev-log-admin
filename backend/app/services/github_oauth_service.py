"""
GitHub OAuth service for authentication and token management
"""
import secrets
from datetime import datetime, timezone
from typing import Optional, Tuple
from uuid import uuid4
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.encryption import get_token_encryption
from app.models.user import User
from app.models.github import GitHubConnection, GitHubConnectionStatus


class GitHubOAuthError(Exception):
    """GitHub OAuth error"""
    pass


class GitHubOAuthService:
    """
    Service for GitHub OAuth authentication.
    Handles OAuth flow, token exchange, and connection management.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.encryption = get_token_encryption()

    def generate_oauth_url(
        self,
        scopes: list[str] = None,
        redirect_uri: str = None
    ) -> Tuple[str, str]:
        """
        Generate GitHub OAuth authorization URL.

        Args:
            scopes: OAuth scopes to request
            redirect_uri: Custom redirect URI

        Returns:
            Tuple of (authorization_url, state)
        """
        if not settings.GITHUB_CLIENT_ID:
            raise GitHubOAuthError("GitHub OAuth is not configured")

        state = secrets.token_urlsafe(32)
        scopes = scopes or ["repo", "read:user", "user:email"]

        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": redirect_uri or settings.GITHUB_CALLBACK_URL,
            "scope": " ".join(scopes),
            "state": state,
            "allow_signup": "true",
        }

        authorization_url = f"{settings.GITHUB_OAUTH_URL}/authorize?{urlencode(params)}"
        return authorization_url, state

    async def exchange_code_for_token(self, code: str) -> dict:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from GitHub callback

        Returns:
            Token response with access_token, token_type, scope

        Raises:
            GitHubOAuthError: If token exchange fails
        """
        if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
            raise GitHubOAuthError("GitHub OAuth is not configured")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.GITHUB_OAUTH_URL}/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                },
                headers={"Accept": "application/json"},
                timeout=30.0,
            )

            if response.status_code != 200:
                raise GitHubOAuthError(
                    f"Failed to exchange code: {response.status_code}"
                )

            data = response.json()

            if "error" in data:
                raise GitHubOAuthError(
                    f"OAuth error: {data.get('error_description', data['error'])}"
                )

            return data

    async def get_github_user(self, access_token: str) -> dict:
        """
        Get GitHub user info using access token.

        Args:
            access_token: GitHub access token

        Returns:
            GitHub user info

        Raises:
            GitHubOAuthError: If API call fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.GITHUB_API_BASE_URL}/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=30.0,
            )

            if response.status_code != 200:
                raise GitHubOAuthError(
                    f"Failed to get user info: {response.status_code}"
                )

            return response.json()

    async def get_github_user_emails(self, access_token: str) -> list[dict]:
        """
        Get GitHub user emails.

        Args:
            access_token: GitHub access token

        Returns:
            List of email objects

        Raises:
            GitHubOAuthError: If API call fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.GITHUB_API_BASE_URL}/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=30.0,
            )

            if response.status_code != 200:
                # Email scope might not be granted
                return []

            return response.json()

    async def create_or_update_connection(
        self,
        user: User,
        access_token: str,
        scopes: str = None,
        refresh_token: str = None,
        token_expires_at: datetime = None,
    ) -> GitHubConnection:
        """
        Create or update GitHub connection for a user.

        Args:
            user: User to create connection for
            access_token: GitHub access token
            scopes: OAuth scopes granted
            refresh_token: Optional refresh token
            token_expires_at: Token expiration time

        Returns:
            Created or updated GitHubConnection
        """
        # Get GitHub user info
        github_user = await self.get_github_user(access_token)

        # Try to get primary email
        github_email = github_user.get("email")
        if not github_email:
            emails = await self.get_github_user_emails(access_token)
            for email_obj in emails:
                if email_obj.get("primary") and email_obj.get("verified"):
                    github_email = email_obj.get("email")
                    break

        # Check for existing connection
        result = await self.db.execute(
            select(GitHubConnection).where(GitHubConnection.user_id == user.id)
        )
        connection = result.scalar_one_or_none()

        # Encrypt tokens
        encrypted_access_token = self.encryption.encrypt(access_token)
        encrypted_refresh_token = (
            self.encryption.encrypt(refresh_token) if refresh_token else None
        )

        if connection:
            # Update existing connection
            connection.github_user_id = str(github_user["id"])
            connection.github_username = github_user["login"]
            connection.github_email = github_email
            connection.github_avatar_url = github_user.get("avatar_url")
            connection.access_token_encrypted = encrypted_access_token
            connection.refresh_token_encrypted = encrypted_refresh_token
            connection.token_expires_at = token_expires_at
            connection.scopes = scopes
            connection.status = GitHubConnectionStatus.ACTIVE.value
            connection.last_used_at = datetime.now(timezone.utc)
        else:
            # Create new connection
            connection = GitHubConnection(
                id=str(uuid4()),
                user_id=user.id,
                github_user_id=str(github_user["id"]),
                github_username=github_user["login"],
                github_email=github_email,
                github_avatar_url=github_user.get("avatar_url"),
                access_token_encrypted=encrypted_access_token,
                refresh_token_encrypted=encrypted_refresh_token,
                token_expires_at=token_expires_at,
                scopes=scopes,
                status=GitHubConnectionStatus.ACTIVE.value,
                last_used_at=datetime.now(timezone.utc),
            )
            self.db.add(connection)

        # Update user's github_username if not set
        if not user.github_username:
            user.github_username = github_user["login"]

        await self.db.flush()
        await self.db.refresh(connection)

        return connection

    async def get_connection(self, user_id: str) -> Optional[GitHubConnection]:
        """
        Get GitHub connection for a user.

        Args:
            user_id: User ID

        Returns:
            GitHubConnection if exists, None otherwise
        """
        result = await self.db.execute(
            select(GitHubConnection).where(
                GitHubConnection.user_id == user_id,
                GitHubConnection.status == GitHubConnectionStatus.ACTIVE.value,
            )
        )
        return result.scalar_one_or_none()

    async def get_decrypted_token(self, user_id: str) -> Optional[str]:
        """
        Get decrypted access token for a user.

        Args:
            user_id: User ID

        Returns:
            Decrypted access token if connection exists, None otherwise
        """
        connection = await self.get_connection(user_id)
        if not connection:
            return None

        try:
            return self.encryption.decrypt(connection.access_token_encrypted)
        except ValueError:
            # Token decryption failed, mark as expired
            connection.status = GitHubConnectionStatus.EXPIRED.value
            await self.db.flush()
            return None

    async def revoke_connection(self, user_id: str) -> bool:
        """
        Revoke GitHub connection for a user.

        Args:
            user_id: User ID

        Returns:
            True if connection was revoked, False if not found
        """
        connection = await self.get_connection(user_id)
        if not connection:
            return False

        connection.status = GitHubConnectionStatus.REVOKED.value
        await self.db.flush()
        return True

    async def update_last_used(self, connection: GitHubConnection) -> None:
        """Update connection's last used timestamp"""
        connection.last_used_at = datetime.now(timezone.utc)
        await self.db.flush()
