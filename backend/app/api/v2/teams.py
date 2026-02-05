"""
Team API endpoints
"""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamWithMembers,
    TeamMemberCreate,
    TeamMemberUpdate,
    TeamMemberResponse,
)
from app.services.team_service import TeamService, TeamError
from app.services.user_service import UserService
from app.middleware.auth import CurrentUser
from app.core.deps import require_team_member, require_team_admin, require_team_owner


router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    data: TeamCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Create a new team

    The creating user becomes the team owner.
    """
    team_service = TeamService(db)

    try:
        team = await team_service.create_team(data, current_user)
        return team
    except TeamError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[TeamResponse])
async def list_my_teams(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    List teams the current user is a member of
    """
    team_service = TeamService(db)
    teams = await team_service.get_user_teams(current_user)
    return teams


@router.get("/{team_id}", response_model=TeamWithMembers)
async def get_team(
    team_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get team details

    Requires team membership.
    """
    team, membership = await require_team_member(team_id, current_user, db)
    team_service = TeamService(db)

    members = await team_service.get_team_members(team)
    member_count = await team_service.get_member_count(team)

    return {
        **TeamResponse.model_validate(team).model_dump(),
        "members": [
            {
                "user_id": m.user_id,
                "team_id": m.team_id,
                "role": m.role,
                "is_active": m.is_active,
                "user_email": m.user.email if m.user else None,
                "user_name": m.user.name if m.user else None,
                "user_avatar_url": m.user.avatar_url if m.user else None,
                "created_at": m.created_at,
                "updated_at": m.updated_at,
            }
            for m in members
        ],
        "member_count": member_count
    }


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    data: TeamUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update team information

    Requires admin privileges.
    """
    team, membership = await require_team_admin(team_id, current_user, db)
    team_service = TeamService(db)

    return await team_service.update_team(team, data)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Delete a team

    Requires owner privileges. This will also delete all team projects.
    """
    team, membership = await require_team_owner(team_id, current_user, db)
    team_service = TeamService(db)

    await team_service.delete_team(team)


# Team Members

@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
async def list_team_members(
    team_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    List team members

    Requires team membership.
    """
    team, membership = await require_team_member(team_id, current_user, db)
    team_service = TeamService(db)

    members = await team_service.get_team_members(team)
    return [
        {
            "user_id": m.user_id,
            "team_id": m.team_id,
            "role": m.role,
            "is_active": m.is_active,
            "user_email": m.user.email if m.user else None,
            "user_name": m.user.name if m.user else None,
            "user_avatar_url": m.user.avatar_url if m.user else None,
            "created_at": m.created_at,
            "updated_at": m.updated_at,
        }
        for m in members
    ]


@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    team_id: str,
    data: TeamMemberCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Add a member to team by email

    Requires admin privileges.
    """
    team, membership = await require_team_admin(team_id, current_user, db)

    # Find user by email
    user_service = UserService(db)
    user = await user_service.get_by_email(data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{data.email}' not found"
        )

    team_service = TeamService(db)

    try:
        member = await team_service.add_member(
            team=team,
            user=user,
            role=data.role,
            invited_by=current_user
        )
        return {
            "user_id": member.user_id,
            "team_id": member.team_id,
            "role": member.role,
            "is_active": member.is_active,
            "user_email": user.email,
            "user_name": user.name,
            "user_avatar_url": user.avatar_url,
            "created_at": member.created_at,
            "updated_at": member.updated_at,
        }
    except TeamError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{team_id}/members/{user_id}", response_model=TeamMemberResponse)
async def update_team_member(
    team_id: str,
    user_id: str,
    data: TeamMemberUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update team member role

    Requires admin privileges.
    """
    team, membership = await require_team_admin(team_id, current_user, db)
    team_service = TeamService(db)

    try:
        member = await team_service.update_member_role(team, user_id, data.role)

        # Get user info
        user_service = UserService(db)
        user = await user_service.get_by_id(user_id)

        return {
            "user_id": member.user_id,
            "team_id": member.team_id,
            "role": member.role,
            "is_active": member.is_active,
            "user_email": user.email if user else None,
            "user_name": user.name if user else None,
            "user_avatar_url": user.avatar_url if user else None,
            "created_at": member.created_at,
            "updated_at": member.updated_at,
        }
    except TeamError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_id: str,
    user_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Remove a member from team

    Requires admin privileges (or self-removal).
    """
    team, membership = await require_team_member(team_id, current_user, db)

    # Allow self-removal or admin removal
    if user_id != current_user.id and not membership.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to remove other members"
        )

    team_service = TeamService(db)

    try:
        await team_service.remove_member(team, user_id)
    except TeamError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{team_id}/transfer-ownership", status_code=status.HTTP_204_NO_CONTENT)
async def transfer_team_ownership(
    team_id: str,
    new_owner_id: str = Query(..., description="User ID of new owner"),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Transfer team ownership to another member

    Requires owner privileges.
    """
    team, membership = await require_team_owner(team_id, current_user, db)
    team_service = TeamService(db)

    try:
        await team_service.transfer_ownership(team, current_user, new_owner_id)
    except TeamError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
