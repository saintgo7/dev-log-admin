"""
Project API endpoints (v2 - with authentication)
"""
import json
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.project import Project
from app.models.commit import Commit
from app.models.team import TeamMember
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithStats,
)
from app.schemas.commit import CommitResponse, CommitListResponse, CommitDetail
from app.middleware.auth import CurrentUser, CurrentUserOptional
from app.core.deps import require_project_access, require_project_write, require_team_member


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Create a new project

    Requires team membership with write access.
    """
    # Verify team membership
    team, membership = await require_team_member(data.team_id, current_user, db)

    if not membership.can_write:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Write access required"
        )

    # Check slug uniqueness
    result = await db.execute(
        select(Project).where(Project.slug == data.slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project slug '{data.slug}' already exists"
        )

    # Create project
    from uuid import uuid4
    project = Project(
        id=str(uuid4()),
        slug=data.slug,
        name=data.name,
        description=data.description,
        repository_url=data.repository_url,
        html_url=data.html_url,
        tech_stack=json.dumps(data.tech_stack) if data.tech_stack else None,
        team_id=data.team_id,
        visibility=data.visibility
    )

    db.add(project)
    await db.flush()
    await db.refresh(project)

    return _project_response(project)


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: CurrentUserOptional,
    db: Annotated[AsyncSession, Depends(get_db)],
    team_id: Optional[str] = Query(None, description="Filter by team"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List projects

    - Public projects are visible to everyone
    - Private projects require team membership
    """
    query = select(Project)

    if team_id:
        # Filter by team
        query = query.where(Project.team_id == team_id)

        # If authenticated, check membership
        if current_user:
            result = await db.execute(
                select(TeamMember).where(
                    TeamMember.team_id == team_id,
                    TeamMember.user_id == current_user.id,
                    TeamMember.is_active == True
                )
            )
            if result.scalar_one_or_none():
                # Member - see all projects
                pass
            else:
                # Non-member - only public
                query = query.where(Project.visibility == "public")
        else:
            # Anonymous - only public
            query = query.where(Project.visibility == "public")
    else:
        # No team filter
        if current_user:
            # Get user's teams
            team_result = await db.execute(
                select(TeamMember.team_id).where(
                    TeamMember.user_id == current_user.id,
                    TeamMember.is_active == True
                )
            )
            user_team_ids = [r[0] for r in team_result.fetchall()]

            # Projects user can see: public OR in user's teams
            query = query.where(
                (Project.visibility == "public") |
                (Project.team_id.in_(user_team_ids))
            )
        else:
            # Anonymous - only public
            query = query.where(Project.visibility == "public")

    query = query.order_by(Project.name)
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    projects = result.scalars().all()

    return [_project_response(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectWithStats)
async def get_project(
    project_id: str,
    current_user: CurrentUserOptional,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get project details with statistics
    """
    project = await require_project_access(project_id, current_user, db)

    # Get type statistics
    type_stats_result = await db.execute(
        select(Commit.type, func.count(Commit.id))
        .where(Commit.project_id == project.id)
        .group_by(Commit.type)
    )
    type_stats = {row[0]: row[1] for row in type_stats_result.fetchall()}

    # Get recent commits
    recent_result = await db.execute(
        select(Commit)
        .where(Commit.project_id == project.id)
        .order_by(Commit.date.desc())
        .limit(5)
    )
    recent_commits = [
        {
            "id": c.id,
            "title": c.title,
            "type": c.type,
            "date": c.date,
            "author_name": c.author_name
        }
        for c in recent_result.scalars().all()
    ]

    response = _project_response(project)
    response["type_stats"] = type_stats
    response["recent_commits"] = recent_commits

    return response


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update project

    Requires write access.
    """
    project = await require_project_write(project_id, current_user, db)

    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.repository_url is not None:
        project.repository_url = data.repository_url
    if data.html_url is not None:
        project.html_url = data.html_url
    if data.tech_stack is not None:
        project.tech_stack = json.dumps(data.tech_stack)
    if data.visibility is not None:
        project.visibility = data.visibility

    await db.flush()
    await db.refresh(project)

    return _project_response(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Delete project

    Requires write access.
    """
    project = await require_project_write(project_id, current_user, db)
    await db.delete(project)
    await db.flush()


# Commits under project

@router.get("/{project_id}/commits", response_model=CommitListResponse)
async def list_project_commits(
    project_id: str,
    current_user: CurrentUserOptional,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    type: Optional[str] = Query(None, description="Filter by commit type"),
    search: Optional[str] = Query(None, description="Search in title/content")
):
    """
    List commits for a project
    """
    project = await require_project_access(project_id, current_user, db)

    query = select(Commit).where(Commit.project_id == project.id)

    if type:
        query = query.where(Commit.type == type)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Commit.title.ilike(search_term)) |
            (Commit.full_content.ilike(search_term))
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get results
    query = query.order_by(Commit.date.desc())
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    commits = result.scalars().all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "commits": [CommitResponse.model_validate(c) for c in commits]
    }


@router.get("/{project_id}/commits/{commit_id}", response_model=CommitDetail)
async def get_commit(
    project_id: str,
    commit_id: int,
    current_user: CurrentUserOptional,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get commit details
    """
    project = await require_project_access(project_id, current_user, db)

    result = await db.execute(
        select(Commit).where(
            Commit.id == commit_id,
            Commit.project_id == project.id
        )
    )
    commit = result.scalar_one_or_none()

    if not commit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commit not found"
        )

    return {
        **CommitResponse.model_validate(commit).model_dump(),
        "full_content": commit.full_content,
        "project_slug": project.slug,
        "project_name": project.name
    }


def _project_response(project: Project) -> dict:
    """Convert project to response dict"""
    tech_stack = None
    if project.tech_stack:
        try:
            tech_stack = json.loads(project.tech_stack)
        except json.JSONDecodeError:
            tech_stack = []

    return {
        "id": project.id,
        "slug": project.slug,
        "name": project.name,
        "description": project.description,
        "repository_url": project.repository_url,
        "html_url": project.html_url,
        "tech_stack": tech_stack,
        "total_commits": project.total_commits,
        "last_synced_at": project.last_synced_at,
        "team_id": project.team_id,
        "visibility": project.visibility,
        "created_at": project.created_at,
        "updated_at": project.updated_at
    }
