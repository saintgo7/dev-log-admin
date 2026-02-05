"""
Team service
"""
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.team import Team, TeamMember, TeamMemberRole
from app.models.user import User
from app.schemas.team import TeamCreate, TeamUpdate, TeamMemberCreate


class TeamError(Exception):
    """Team operation error"""
    pass


class TeamService:
    """Service for team operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_team(
        self,
        data: TeamCreate,
        owner: User
    ) -> Team:
        """
        Create a new team

        Args:
            data: Team creation data
            owner: User who will be the owner

        Returns:
            Created team

        Raises:
            TeamError: If slug already exists
        """
        # Check slug uniqueness
        result = await self.db.execute(
            select(Team).where(Team.slug == data.slug)
        )
        if result.scalar_one_or_none():
            raise TeamError(f"Team slug '{data.slug}' already exists")

        # Create team
        team = Team(
            id=str(uuid4()),
            name=data.name,
            slug=data.slug,
            description=data.description,
            avatar_url=data.avatar_url
        )
        self.db.add(team)
        await self.db.flush()

        # Add owner as team member
        membership = TeamMember(
            team_id=team.id,
            user_id=owner.id,
            role=TeamMemberRole.OWNER.value,
            is_active=True
        )
        self.db.add(membership)
        await self.db.flush()

        await self.db.refresh(team)
        return team

    async def update_team(
        self,
        team: Team,
        data: TeamUpdate
    ) -> Team:
        """
        Update team information

        Args:
            team: Team to update
            data: Update data

        Returns:
            Updated team
        """
        if data.name is not None:
            team.name = data.name
        if data.description is not None:
            team.description = data.description
        if data.avatar_url is not None:
            team.avatar_url = data.avatar_url

        await self.db.flush()
        await self.db.refresh(team)
        return team

    async def delete_team(self, team: Team) -> None:
        """
        Delete a team

        Args:
            team: Team to delete
        """
        await self.db.delete(team)
        await self.db.flush()

    async def get_team_by_slug(self, slug: str) -> Optional[Team]:
        """Get team by slug"""
        result = await self.db.execute(
            select(Team).where(Team.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_user_teams(self, user: User) -> List[Team]:
        """
        Get all teams the user is a member of

        Args:
            user: User

        Returns:
            List of teams
        """
        result = await self.db.execute(
            select(Team)
            .join(TeamMember)
            .where(
                TeamMember.user_id == user.id,
                TeamMember.is_active == True
            )
            .options(selectinload(Team.members))
        )
        return list(result.scalars().all())

    async def get_team_members(self, team: Team) -> List[TeamMember]:
        """
        Get all members of a team

        Args:
            team: Team

        Returns:
            List of team members with user info
        """
        result = await self.db.execute(
            select(TeamMember)
            .where(TeamMember.team_id == team.id)
            .options(selectinload(TeamMember.user))
        )
        return list(result.scalars().all())

    async def add_member(
        self,
        team: Team,
        user: User,
        role: str = TeamMemberRole.MEMBER.value,
        invited_by: Optional[User] = None
    ) -> TeamMember:
        """
        Add a member to team

        Args:
            team: Team
            user: User to add
            role: Member role
            invited_by: User who invited

        Returns:
            Team membership

        Raises:
            TeamError: If user is already a member
        """
        # Check if already member
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team.id,
                TeamMember.user_id == user.id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            if existing.is_active:
                raise TeamError("User is already a member of this team")
            # Reactivate membership
            existing.is_active = True
            existing.role = role
            await self.db.flush()
            return existing

        # Create membership
        membership = TeamMember(
            team_id=team.id,
            user_id=user.id,
            role=role,
            is_active=True,
            invited_by=invited_by.id if invited_by else None
        )
        self.db.add(membership)
        await self.db.flush()

        return membership

    async def update_member_role(
        self,
        team: Team,
        user_id: str,
        new_role: str
    ) -> TeamMember:
        """
        Update member role

        Args:
            team: Team
            user_id: User ID
            new_role: New role

        Returns:
            Updated membership

        Raises:
            TeamError: If member not found or trying to change owner
        """
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team.id,
                TeamMember.user_id == user_id
            )
        )
        membership = result.scalar_one_or_none()

        if not membership:
            raise TeamError("Member not found")

        # Can't change owner role directly (use transfer ownership)
        if membership.role == TeamMemberRole.OWNER.value:
            raise TeamError("Cannot change owner role. Use transfer ownership instead.")

        # Can't promote to owner
        if new_role == TeamMemberRole.OWNER.value:
            raise TeamError("Cannot promote to owner. Use transfer ownership instead.")

        membership.role = new_role
        await self.db.flush()

        return membership

    async def remove_member(
        self,
        team: Team,
        user_id: str
    ) -> None:
        """
        Remove member from team

        Args:
            team: Team
            user_id: User ID to remove

        Raises:
            TeamError: If member not found or trying to remove owner
        """
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team.id,
                TeamMember.user_id == user_id
            )
        )
        membership = result.scalar_one_or_none()

        if not membership:
            raise TeamError("Member not found")

        if membership.role == TeamMemberRole.OWNER.value:
            raise TeamError("Cannot remove team owner")

        membership.is_active = False
        await self.db.flush()

    async def transfer_ownership(
        self,
        team: Team,
        current_owner: User,
        new_owner_id: str
    ) -> None:
        """
        Transfer team ownership

        Args:
            team: Team
            current_owner: Current owner
            new_owner_id: New owner user ID

        Raises:
            TeamError: If transfer fails
        """
        # Get current owner membership
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team.id,
                TeamMember.user_id == current_owner.id
            )
        )
        current_membership = result.scalar_one_or_none()

        if not current_membership or current_membership.role != TeamMemberRole.OWNER.value:
            raise TeamError("Not the team owner")

        # Get new owner membership
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team.id,
                TeamMember.user_id == new_owner_id,
                TeamMember.is_active == True
            )
        )
        new_membership = result.scalar_one_or_none()

        if not new_membership:
            raise TeamError("New owner must be an active team member")

        # Transfer
        current_membership.role = TeamMemberRole.ADMIN.value
        new_membership.role = TeamMemberRole.OWNER.value
        await self.db.flush()

    async def get_member_count(self, team: Team) -> int:
        """Get active member count for team"""
        result = await self.db.execute(
            select(func.count())
            .select_from(TeamMember)
            .where(
                TeamMember.team_id == team.id,
                TeamMember.is_active == True
            )
        )
        return result.scalar() or 0
