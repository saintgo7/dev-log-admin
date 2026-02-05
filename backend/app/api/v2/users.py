"""
User API endpoints
"""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserResponse, UserUpdate, UserWithTeams
from app.services.user_service import UserService
from app.services.team_service import TeamService
from app.middleware.auth import CurrentUser, CurrentAdminUser


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserWithTeams)
async def get_my_profile(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get current user profile with team memberships
    """
    team_service = TeamService(db)
    teams = await team_service.get_user_teams(current_user)

    return {
        **UserResponse.model_validate(current_user).model_dump(),
        "teams": [
            {
                "team_id": t.id,
                "team_name": t.name,
                "team_slug": t.slug,
                "role": next(
                    (m.role for m in t.members if m.user_id == current_user.id),
                    "member"
                )
            }
            for t in teams
        ]
    }


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    data: UserUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update current user profile
    """
    user_service = UserService(db)
    return await user_service.update_user(current_user, data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get user by ID

    Requires authentication. Only admins can see full details.
    """
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# Admin endpoints

@router.get("", response_model=List[UserResponse])
async def list_users(
    current_user: CurrentAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str = Query(None)
):
    """
    List all users (admin only)
    """
    user_service = UserService(db)
    users, total = await user_service.list_users(
        limit=limit,
        offset=offset,
        search=search
    )
    return users


@router.post("/{user_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: str,
    current_user: CurrentAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Deactivate a user account (admin only)
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await user_service.deactivate_user(user)


@router.post("/{user_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
async def activate_user(
    user_id: str,
    current_user: CurrentAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Activate a user account (admin only)
    """
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await user_service.activate_user(user)
