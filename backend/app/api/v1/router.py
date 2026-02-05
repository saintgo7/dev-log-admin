"""
API v1 Router - Legacy compatibility (read-only, no auth required)

This router provides backward compatibility with the original API.
All endpoints are read-only and don't require authentication.
"""
import json
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.project import Project
from app.models.commit import Commit


router = APIRouter(prefix="/api", tags=["Legacy API (v1)"])


@router.get("/projects")
async def list_projects(db: AsyncSession = Depends(get_db)):
    """Get all projects (legacy endpoint)"""
    result = await db.execute(
        select(Project).order_by(Project.name)
    )
    projects = result.scalars().all()

    return [
        {
            "id": p.id,
            "slug": p.slug,
            "name": p.name,
            "description": p.description,
            "repository_url": p.repository_url,
            "tech_stack": json.loads(p.tech_stack) if p.tech_stack else [],
            "html_url": p.html_url,
            "total_commits": p.total_commits,
            "last_synced_at": p.last_synced_at.isoformat() if p.last_synced_at else None
        }
        for p in projects
    ]


@router.get("/projects/{slug}")
async def get_project(slug: str, db: AsyncSession = Depends(get_db)):
    """Get project details by slug (legacy endpoint)"""
    result = await db.execute(
        select(Project).where(Project.slug == slug)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get type statistics
    type_stats_result = await db.execute(
        select(Commit.type, func.count(Commit.id))
        .where(Commit.project_id == project.id)
        .group_by(Commit.type)
    )
    type_stats = {row[0]: row[1] for row in type_stats_result.fetchall()}

    return {
        "id": project.id,
        "slug": project.slug,
        "name": project.name,
        "description": project.description,
        "repository_url": project.repository_url,
        "tech_stack": json.loads(project.tech_stack) if project.tech_stack else [],
        "html_url": project.html_url,
        "total_commits": project.total_commits,
        "last_synced_at": project.last_synced_at.isoformat() if project.last_synced_at else None,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        "type_stats": type_stats
    }


@router.get("/projects/{slug}/commits")
async def get_project_commits(
    slug: str,
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
    type: Optional[str] = None,
    search: Optional[str] = None
):
    """Get commits for a project (legacy endpoint)"""
    result = await db.execute(
        select(Project).where(Project.slug == slug)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

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
        "commits": [
            {
                "id": c.id,
                "log_number": c.log_number,
                "commit_hash": c.commit_hash,
                "type": c.type,
                "title": c.title,
                "author_name": c.author_name,
                "author_email": c.author_email,
                "date": c.date.isoformat() if c.date else None,
                "files_changed": c.files_changed,
                "lines_added": c.lines_added,
                "lines_deleted": c.lines_deleted
            }
            for c in commits
        ]
    }


@router.get("/commits/{commit_id}")
async def get_commit_detail(commit_id: int, db: AsyncSession = Depends(get_db)):
    """Get full commit details (legacy endpoint)"""
    result = await db.execute(
        select(Commit, Project)
        .join(Project)
        .where(Commit.id == commit_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Commit not found")

    commit, project = row

    return {
        "id": commit.id,
        "project_id": commit.project_id,
        "project_slug": project.slug,
        "project_name": project.name,
        "log_number": commit.log_number,
        "commit_hash": commit.commit_hash,
        "type": commit.type,
        "title": commit.title,
        "author_name": commit.author_name,
        "author_email": commit.author_email,
        "date": commit.date.isoformat() if commit.date else None,
        "files_changed": commit.files_changed,
        "lines_added": commit.lines_added,
        "lines_deleted": commit.lines_deleted,
        "full_content": commit.full_content,
        "created_at": commit.created_at.isoformat() if commit.created_at else None
    }


@router.get("/search")
async def search_commits(
    q: str,
    db: AsyncSession = Depends(get_db),
    project: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Search commits across all projects (legacy endpoint)"""
    search_term = f"%{q}%"

    query = (
        select(Commit, Project)
        .join(Project)
        .where(
            (Commit.title.ilike(search_term)) |
            (Commit.full_content.ilike(search_term))
        )
    )

    if project:
        query = query.where(Project.slug == project)

    if type:
        query = query.where(Commit.type == type)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get results
    query = query.order_by(Commit.date.desc())
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    rows = result.fetchall()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "query": q,
        "results": [
            {
                "id": commit.id,
                "log_number": commit.log_number,
                "commit_hash": commit.commit_hash,
                "type": commit.type,
                "title": commit.title,
                "author_name": commit.author_name,
                "date": commit.date.isoformat() if commit.date else None,
                "files_changed": commit.files_changed,
                "lines_added": commit.lines_added,
                "lines_deleted": commit.lines_deleted,
                "project_slug": proj.slug,
                "project_name": proj.name
            }
            for commit, proj in rows
        ]
    }


@router.get("/stats/overview")
async def get_overview_stats(db: AsyncSession = Depends(get_db)):
    """Get overall statistics (legacy endpoint)"""
    # Total projects
    project_count = await db.execute(select(func.count()).select_from(Project))
    total_projects = project_count.scalar() or 0

    # Total commits
    commit_count = await db.execute(select(func.count()).select_from(Commit))
    total_commits = commit_count.scalar() or 0

    # Commits by type
    type_stats_result = await db.execute(
        select(Commit.type, func.count(Commit.id))
        .group_by(Commit.type)
        .order_by(func.count(Commit.id).desc())
    )
    commits_by_type = {row[0]: row[1] for row in type_stats_result.fetchall()}

    # Recent activity
    recent_result = await db.execute(
        select(Commit, Project)
        .join(Project)
        .order_by(Commit.date.desc())
        .limit(20)
    )
    recent_activity = [
        {
            "id": commit.id,
            "log_number": commit.log_number,
            "title": commit.title,
            "type": commit.type,
            "date": commit.date.isoformat() if commit.date else None,
            "project_slug": proj.slug,
            "project_name": proj.name
        }
        for commit, proj in recent_result.fetchall()
    ]

    # Commits by project
    project_stats_result = await db.execute(
        select(Project.name, Project.slug, func.count(Commit.id))
        .outerjoin(Commit)
        .group_by(Project.id)
        .order_by(func.count(Commit.id).desc())
    )
    commits_by_project = [
        {"name": row[0], "slug": row[1], "commit_count": row[2]}
        for row in project_stats_result.fetchall()
    ]

    return {
        "total_projects": total_projects,
        "total_commits": total_commits,
        "commits_by_type": commits_by_type,
        "recent_activity": recent_activity,
        "commits_by_project": commits_by_project
    }


@router.get("/stats/timeline")
async def get_timeline_stats(
    db: AsyncSession = Depends(get_db),
    days: int = 30
):
    """Get commit timeline statistics (legacy endpoint)"""
    from datetime import datetime, timedelta, timezone

    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(
            func.date(Commit.date).label("day"),
            func.count(Commit.id).label("count"),
            func.string_agg(Commit.type.distinct(), ",").label("types")
        )
        .where(Commit.date >= start_date)
        .group_by(func.date(Commit.date))
        .order_by(func.date(Commit.date).desc())
    )

    return {
        "days": days,
        "timeline": [
            {
                "day": row[0].isoformat() if row[0] else None,
                "count": row[1],
                "types": row[2]
            }
            for row in result.fetchall()
        ]
    }


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    try:
        await db.execute(select(1))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
