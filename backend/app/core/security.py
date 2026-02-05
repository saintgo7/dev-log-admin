"""
Security utilities - JWT, password hashing, OAuth
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityError(Exception):
    """Base security exception"""
    pass


class TokenExpiredError(SecurityError):
    """Token has expired"""
    pass


class InvalidTokenError(SecurityError):
    """Token is invalid"""
    pass


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str | UUID,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a JWT access token

    Args:
        subject: User ID or other identifier
        expires_delta: Custom expiration time
        additional_claims: Additional claims to include in token

    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }

    if additional_claims:
        to_encode.update(additional_claims)

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(subject: str | UUID) -> str:
    """
    Create a JWT refresh token with longer expiration

    Args:
        subject: User ID or other identifier

    Returns:
        Encoded JWT refresh token string
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        TokenExpiredError: If token has expired
        InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except JWTError as e:
        raise InvalidTokenError(f"Invalid token: {str(e)}")


def verify_token(token: str, token_type: str = "access") -> str:
    """
    Verify token and return subject (user_id)

    Args:
        token: JWT token string
        token_type: Expected token type ('access' or 'refresh')

    Returns:
        Subject (user_id) from token

    Raises:
        InvalidTokenError: If token type doesn't match
    """
    payload = decode_token(token)

    if payload.get("type") != token_type:
        raise InvalidTokenError(f"Expected {token_type} token, got {payload.get('type')}")

    subject = payload.get("sub")
    if not subject:
        raise InvalidTokenError("Token missing subject")

    return subject
