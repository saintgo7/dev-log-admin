"""
Authentication schemas
"""
from typing import Optional

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema


class Token(BaseSchema):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token expiration time in seconds")


class TokenPayload(BaseSchema):
    """JWT token payload"""
    sub: str  # User ID
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp
    type: str  # Token type (access/refresh)


class LoginRequest(BaseSchema):
    """Email/password login request"""
    email: EmailStr
    password: str = Field(min_length=8)


class RegisterRequest(BaseSchema):
    """User registration request"""
    email: EmailStr
    password: str = Field(min_length=8)
    name: Optional[str] = Field(None, max_length=255)


class OAuthCallback(BaseSchema):
    """OAuth callback data"""
    code: str
    state: Optional[str] = None


class RefreshTokenRequest(BaseSchema):
    """Refresh token request"""
    refresh_token: str


class PasswordResetRequest(BaseSchema):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(min_length=8)


class PasswordChangeRequest(BaseSchema):
    """Password change request (authenticated user)"""
    current_password: str
    new_password: str = Field(min_length=8)
