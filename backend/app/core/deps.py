"""
Common dependencies for API endpoints
"""
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.team import Team, TeamMember, TeamMemberRole
from app.models.project import Project
from app.middleware.auth import get_current_user, get_current_user_optional


# Type alias for database session
DB = Annotated[AsyncSession, Depends(get_db)]


async def get_team_or_404(
    team_id: Annotated[str, Path(description="Team ID")],
    db: DB
) -> Team:
    """Get team by ID or raise 404"""
    result = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    return team


async def get_team_membership(
    team: Team,
    user: User,
    db: DB
) -> Optional[TeamMember]:
    """Get team membership for user"""
    result = await db.execute(
        select(TeamMember)
        .where(TeamMember.team_id == team.id, TeamMember.user_id == user.id)
    )
    return result.scalar_one_or_none()


async def require_team_member(
    team_id: Annotated[str, Path(description="Team ID")],
    current_user: Annotated[User, Depends(get_current_user)],
    db: DB
) -> tuple[Team, TeamMember]:
    """
    Require current user to be a team member.
    Returns (team, membership) tuple.
    """
    team = await get_team_or_404(team_id, db)
    membership = await get_team_membership(team, current_user, db)

    if not membership or not membership.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this team"
        )

    return team, membership


async def require_team_admin(
    team_id: Annotated[str, Path(description="Team ID")],
    current_user: Annotated[User, Depends(get_current_user)],
    db: DB
) -> tuple[Team, TeamMember]:
    """
    Require current user to be team admin or owner.
    Returns (team, membership) tuple.
    """
    team, membership = await require_team_member(team_id, current_user, db)

    if not membership.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this team"
        )

    return team, membership


async def require_team_owner(
    team_id: Annotated[str, Path(description="Team ID")],
    current_user: Annotated[User, Depends(get_current_user)],
    db: DB
) -> tuple[Team, TeamMember]:
    """
    Require current user to be team owner.
    Returns (team, membership) tuple.
    """
    team, membership = await require_team_member(team_id, current_user, db)

    if not membership.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner privileges required for this team"
        )

    return team, membership


async def get_project_or_404(
    project_id: Annotated[str, Path(description="Project ID")],
    db: DB
) -> Project:
    """Get project by ID or raise 404"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


async def require_project_access(
    project_id: Annotated[str, Path(description="Project ID")],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
    db: DB
) -> Project:
    """
    Require access to project.
    Public projects can be accessed by anyone.
    Private/team projects require team membership.
    """
    project = await get_project_or_404(project_id, db)

    # Public projects are accessible to everyone
    if project.is_public:
        return project

    # Anonymous users can't access non-public projects
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    # Check team membership if project belongs to a team
    if project.team_id:
        membership = await db.execute(
            select(TeamMember)
            .where(
                TeamMember.team_id == project.team_id,
                TeamMember.user_id == current_user.id,
                TeamMember.is_active == True
            )
        )
        if not membership.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project"
            )

    return project


async def require_project_write(
    project_id: Annotated[str, Path(description="Project ID")],
    current_user: Annotated[User, Depends(get_current_user)],
    db: DB
) -> Project:
    """
    Require write access to project.
    Requires team membership with write permission.
    """
    project = await get_project_or_404(project_id, db)

    if not project.team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Project has no team"
        )

    result = await db.execute(
        select(TeamMember)
        .where(
            TeamMember.team_id == project.team_id,
            TeamMember.user_id == current_user.id,
            TeamMember.is_active == True
        )
    )
    membership = result.scalar_one_or_none()

    if not membership or not membership.can_write:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Write access required for this project"
        )

    return project
