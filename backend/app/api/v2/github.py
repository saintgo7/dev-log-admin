"""
GitHub Integration API endpoints
"""
import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import (
    get_db,
    get_current_user,
    require_repository_access,
    require_repository_write,
)
from app.models.user import User
from app.models.github import GitHubRepository, GitHubConnection
from app.schemas.github import (
    GitHubOAuthRequest,
    GitHubOAuthResponse,
    GitHubOAuthCallback,
    GitHubConnectionResponse,
    GitHubConnectionStatus,
    GitHubRepositoryCreate,
    GitHubRepositoryUpdate,
    GitHubRepositoryResponse,
    GitHubRepositoryList,
    GitHubRepositoryBase,
    SyncRequest,
    SyncHistoryResponse,
    SyncStatusResponse,
    WebhookSetupRequest,
    WebhookSetupResponse,
    WebhookEventResponse,
    GitHubRateLimitInfo,
)
from app.services.github_oauth_service import GitHubOAuthService, GitHubOAuthError
from app.services.github_client_service import GitHubClient, GitHubAPIError
from app.services.sync_service import SyncService, SyncError
from app.services.webhook_service import WebhookService, WebhookSignatureError
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/github", tags=["GitHub"])


# ============================================================================
# OAuth Endpoints
# ============================================================================

@router.get("/oauth/authorize", response_model=GitHubOAuthResponse)
async def github_oauth_authorize(
    request: GitHubOAuthRequest = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get GitHub OAuth authorization URL.

    Returns a URL to redirect the user to GitHub for authorization.
    The state parameter should be stored and verified in the callback.
    """
    oauth_service = GitHubOAuthService(db)

    try:
        authorization_url, state = oauth_service.generate_oauth_url(
            scopes=request.scopes,
            redirect_uri=request.redirect_uri,
        )
    except GitHubOAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return GitHubOAuthResponse(
        authorization_url=authorization_url,
        state=state,
    )


@router.post("/oauth/callback", response_model=GitHubConnectionResponse)
async def github_oauth_callback(
    callback: GitHubOAuthCallback,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Handle GitHub OAuth callback.

    Exchange the authorization code for an access token and create
    a GitHub connection for the user.
    """
    oauth_service = GitHubOAuthService(db)

    try:
        # Exchange code for token
        token_response = await oauth_service.exchange_code_for_token(callback.code)

        access_token = token_response.get("access_token")
        scopes = token_response.get("scope", "")
        refresh_token = token_response.get("refresh_token")

        if not access_token:
            raise GitHubOAuthError("No access token in response")

        # Create or update connection
        connection = await oauth_service.create_or_update_connection(
            user=current_user,
            access_token=access_token,
            scopes=scopes,
            refresh_token=refresh_token,
        )

        await db.commit()

        return GitHubConnectionResponse(
            id=connection.id,
            user_id=connection.user_id,
            github_user_id=connection.github_user_id,
            github_username=connection.github_username,
            github_email=connection.github_email,
            github_avatar_url=connection.github_avatar_url,
            status=connection.status,
            scopes=connection.scopes,
            last_used_at=connection.last_used_at,
            created_at=connection.created_at,
            updated_at=connection.updated_at,
        )

    except GitHubOAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/connection", response_model=GitHubConnectionStatus)
async def get_github_connection_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's GitHub connection status"""
    oauth_service = GitHubOAuthService(db)
    connection = await oauth_service.get_connection(current_user.id)

    if not connection:
        return GitHubConnectionStatus(connected=False)

    return GitHubConnectionStatus(
        connected=True,
        connection=GitHubConnectionResponse(
            id=connection.id,
            user_id=connection.user_id,
            github_user_id=connection.github_user_id,
            github_username=connection.github_username,
            github_email=connection.github_email,
            github_avatar_url=connection.github_avatar_url,
            status=connection.status,
            scopes=connection.scopes,
            last_used_at=connection.last_used_at,
            created_at=connection.created_at,
            updated_at=connection.updated_at,
        ),
    )


@router.delete("/connection", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_github_connection(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revoke GitHub connection"""
    oauth_service = GitHubOAuthService(db)
    revoked = await oauth_service.revoke_connection(current_user.id)

    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No GitHub connection found",
        )

    await db.commit()


# ============================================================================
# Repository Endpoints
# ============================================================================

@router.get("/repositories/available", response_model=GitHubRepositoryList)
async def list_available_repositories(
    per_page: int = Query(50, ge=1, le=100),
    max_items: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List GitHub repositories available for linking.

    Returns repositories the user has access to on GitHub.
    """
    sync_service = SyncService(db)

    try:
        repos = await sync_service.list_available_repositories(
            user_id=current_user.id,
            per_page=per_page,
            max_items=max_items,
        )
    except SyncError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return GitHubRepositoryList(
        repositories=[
            GitHubRepositoryBase(
                owner=r["owner"]["login"],
                name=r["name"],
                full_name=r["full_name"],
                description=r.get("description"),
                html_url=r["html_url"],
                default_branch=r.get("default_branch", "main"),
                is_private=r.get("private", False),
                is_fork=r.get("fork", False),
                language=r.get("language"),
            )
            for r in repos
        ],
        total_count=len(repos),
    )


@router.post("/repositories", response_model=GitHubRepositoryResponse, status_code=status.HTTP_201_CREATED)
async def link_repository(
    data: GitHubRepositoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Link a GitHub repository to a project.

    Creates a connection between a local project and a GitHub repository
    for synchronization.
    """
    sync_service = SyncService(db)

    try:
        github_repo = await sync_service.link_repository(
            user_id=current_user.id,
            project_id=data.project_id,
            owner=data.owner,
            name=data.name,
        )
        await db.commit()

        return GitHubRepositoryResponse(
            id=github_repo.id,
            project_id=github_repo.project_id,
            github_repo_id=github_repo.github_repo_id,
            owner=github_repo.owner,
            name=github_repo.name,
            full_name=github_repo.full_name,
            description=github_repo.description,
            html_url=github_repo.html_url,
            clone_url=github_repo.clone_url,
            ssh_url=github_repo.ssh_url,
            default_branch=github_repo.default_branch,
            is_private=github_repo.is_private,
            is_fork=github_repo.is_fork,
            language=github_repo.language,
            topics=github_repo.topics,
            stars_count=github_repo.stars_count,
            forks_count=github_repo.forks_count,
            watchers_count=github_repo.watchers_count,
            open_issues_count=github_repo.open_issues_count,
            sync_enabled=github_repo.sync_enabled,
            sync_commits=github_repo.sync_commits,
            sync_issues=github_repo.sync_issues,
            sync_prs=github_repo.sync_prs,
            last_sync_at=github_repo.last_sync_at,
            last_sync_status=github_repo.last_sync_status,
            last_sync_error=github_repo.last_sync_error,
            last_commit_sha=github_repo.last_commit_sha,
            webhook_active=github_repo.webhook_active,
            created_at=github_repo.created_at,
            updated_at=github_repo.updated_at,
        )

    except SyncError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/repositories/{repository_id}", response_model=GitHubRepositoryResponse)
async def get_repository(
    repository_id: str,
    db: AsyncSession = Depends(get_db),
    github_repo: GitHubRepository = Depends(require_repository_access),
):
    """Get a linked GitHub repository"""
    return GitHubRepositoryResponse(
        id=github_repo.id,
        project_id=github_repo.project_id,
        github_repo_id=github_repo.github_repo_id,
        owner=github_repo.owner,
        name=github_repo.name,
        full_name=github_repo.full_name,
        description=github_repo.description,
        html_url=github_repo.html_url,
        clone_url=github_repo.clone_url,
        ssh_url=github_repo.ssh_url,
        default_branch=github_repo.default_branch,
        is_private=github_repo.is_private,
        is_fork=github_repo.is_fork,
        language=github_repo.language,
        topics=github_repo.topics,
        stars_count=github_repo.stars_count,
        forks_count=github_repo.forks_count,
        watchers_count=github_repo.watchers_count,
        open_issues_count=github_repo.open_issues_count,
        sync_enabled=github_repo.sync_enabled,
        sync_commits=github_repo.sync_commits,
        sync_issues=github_repo.sync_issues,
        sync_prs=github_repo.sync_prs,
        last_sync_at=github_repo.last_sync_at,
        last_sync_status=github_repo.last_sync_status,
        last_sync_error=github_repo.last_sync_error,
        last_commit_sha=github_repo.last_commit_sha,
        webhook_active=github_repo.webhook_active,
        created_at=github_repo.created_at,
        updated_at=github_repo.updated_at,
    )


@router.patch("/repositories/{repository_id}", response_model=GitHubRepositoryResponse)
async def update_repository(
    repository_id: str,
    data: GitHubRepositoryUpdate,
    db: AsyncSession = Depends(get_db),
    github_repo: GitHubRepository = Depends(require_repository_write),
):
    """Update repository sync settings"""
    # Update fields
    if data.sync_enabled is not None:
        github_repo.sync_enabled = data.sync_enabled
    if data.sync_commits is not None:
        github_repo.sync_commits = data.sync_commits
    if data.sync_issues is not None:
        github_repo.sync_issues = data.sync_issues
    if data.sync_prs is not None:
        github_repo.sync_prs = data.sync_prs

    await db.commit()
    await db.refresh(github_repo)

    return GitHubRepositoryResponse(
        id=github_repo.id,
        project_id=github_repo.project_id,
        github_repo_id=github_repo.github_repo_id,
        owner=github_repo.owner,
        name=github_repo.name,
        full_name=github_repo.full_name,
        description=github_repo.description,
        html_url=github_repo.html_url,
        clone_url=github_repo.clone_url,
        ssh_url=github_repo.ssh_url,
        default_branch=github_repo.default_branch,
        is_private=github_repo.is_private,
        is_fork=github_repo.is_fork,
        language=github_repo.language,
        topics=github_repo.topics,
        stars_count=github_repo.stars_count,
        forks_count=github_repo.forks_count,
        watchers_count=github_repo.watchers_count,
        open_issues_count=github_repo.open_issues_count,
        sync_enabled=github_repo.sync_enabled,
        sync_commits=github_repo.sync_commits,
        sync_issues=github_repo.sync_issues,
        sync_prs=github_repo.sync_prs,
        last_sync_at=github_repo.last_sync_at,
        last_sync_status=github_repo.last_sync_status,
        last_sync_error=github_repo.last_sync_error,
        last_commit_sha=github_repo.last_commit_sha,
        webhook_active=github_repo.webhook_active,
        created_at=github_repo.created_at,
        updated_at=github_repo.updated_at,
    )


@router.delete("/repositories/{repository_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_repository(
    repository_id: str,
    db: AsyncSession = Depends(get_db),
    github_repo: GitHubRepository = Depends(require_repository_write),
):
    """Unlink a GitHub repository from a project"""
    await db.delete(github_repo)
    await db.commit()


# ============================================================================
# Sync Endpoints
# ============================================================================

@router.post("/repositories/{repository_id}/sync", response_model=SyncHistoryResponse)
async def sync_repository(
    repository_id: str,
    data: SyncRequest = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    github_repo: GitHubRepository = Depends(require_repository_write),
):
    """
    Trigger a manual sync for a repository.

    Syncs commits, issues, and/or pull requests from GitHub.
    """
    data = data or SyncRequest()
    sync_service = SyncService(db)

    try:
        sync_history = await sync_service.sync_repository(
            user_id=current_user.id,
            repository_id=repository_id,
            sync_commits=data.sync_commits,
            sync_issues=data.sync_issues,
            sync_prs=data.sync_prs,
            full_sync=data.full_sync,
        )
        await db.commit()

        return SyncHistoryResponse(
            id=sync_history.id,
            repository_id=sync_history.repository_id,
            sync_type=sync_history.sync_type,
            status=sync_history.status,
            started_at=sync_history.started_at,
            completed_at=sync_history.completed_at,
            commits_synced=sync_history.commits_synced,
            issues_synced=sync_history.issues_synced,
            prs_synced=sync_history.prs_synced,
            error_message=sync_history.error_message,
            created_at=sync_history.created_at,
            updated_at=sync_history.updated_at,
        )

    except SyncError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/repositories/{repository_id}/sync/status", response_model=SyncStatusResponse)
async def get_sync_status(
    repository_id: str,
    db: AsyncSession = Depends(get_db),
    github_repo: GitHubRepository = Depends(require_repository_access),
):
    """Get sync status for a repository"""
    sync_service = SyncService(db)
    last_sync, pending_count = await sync_service.get_sync_status(repository_id)

    last_sync_response = None
    if last_sync:
        last_sync_response = SyncHistoryResponse(
            id=last_sync.id,
            repository_id=last_sync.repository_id,
            sync_type=last_sync.sync_type,
            status=last_sync.status,
            started_at=last_sync.started_at,
            completed_at=last_sync.completed_at,
            commits_synced=last_sync.commits_synced,
            issues_synced=last_sync.issues_synced,
            prs_synced=last_sync.prs_synced,
            error_message=last_sync.error_message,
            created_at=last_sync.created_at,
            updated_at=last_sync.updated_at,
        )

    return SyncStatusResponse(
        repository_id=repository_id,
        is_syncing=pending_count > 0,
        last_sync=last_sync_response,
        pending_syncs=pending_count,
    )


@router.get("/repositories/{repository_id}/sync/history", response_model=List[SyncHistoryResponse])
async def get_sync_history(
    repository_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    github_repo: GitHubRepository = Depends(require_repository_access),
):
    """Get sync history for a repository"""
    sync_service = SyncService(db)
    history = await sync_service.get_sync_history(repository_id, limit=limit)

    return [
        SyncHistoryResponse(
            id=h.id,
            repository_id=h.repository_id,
            sync_type=h.sync_type,
            status=h.status,
            started_at=h.started_at,
            completed_at=h.completed_at,
            commits_synced=h.commits_synced,
            issues_synced=h.issues_synced,
            prs_synced=h.prs_synced,
            error_message=h.error_message,
            created_at=h.created_at,
            updated_at=h.updated_at,
        )
        for h in history
    ]


# ============================================================================
# Rate Limit
# ============================================================================

@router.get("/rate-limit", response_model=GitHubRateLimitInfo)
async def get_rate_limit(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get GitHub API rate limit status"""
    oauth_service = GitHubOAuthService(db)
    access_token = await oauth_service.get_decrypted_token(current_user.id)

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No GitHub connection found",
        )

    async with GitHubClient(access_token) as client:
        try:
            rate_limit = await client.get_rate_limit()
            return rate_limit
        except GitHubAPIError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
