"""
Authentication API endpoints
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import (
    Token,
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    PasswordChangeRequest,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService, AuthenticationError
from app.middleware.auth import CurrentUser


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Register a new user account

    - **email**: Valid email address
    - **password**: At least 8 characters
    - **name**: Optional display name
    """
    auth_service = AuthService(db)

    try:
        user = await auth_service.register_user(
            email=data.email,
            password=data.password,
            name=data.name
        )
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Login with email and password

    Returns access and refresh tokens
    """
    auth_service = AuthService(db)

    try:
        user = await auth_service.authenticate_user(
            email=data.email,
            password=data.password
        )
        return await auth_service.create_tokens(user)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    data: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Refresh access token using refresh token
    """
    auth_service = AuthService(db)

    try:
        return await auth_service.refresh_tokens(data.refresh_token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """
    Get current authenticated user information
    """
    return current_user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: PasswordChangeRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Change password for current user
    """
    auth_service = AuthService(db)

    try:
        await auth_service.change_password(
            user=current_user,
            current_password=data.current_password,
            new_password=data.new_password
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: CurrentUser):
    """
    Logout current user

    Note: JWT tokens are stateless. This endpoint is provided for
    frontend convenience. Client should discard tokens.
    """
    # In a stateful implementation, you would invalidate the token here
    # For now, this is a no-op - client should discard tokens
    pass
