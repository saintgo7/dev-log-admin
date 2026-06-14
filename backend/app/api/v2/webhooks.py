"""
Webhook endpoints for external integrations
"""
import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request, Query, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.github import WebhookEventResponse
from app.services.webhook_service import (
    WebhookService,
    WebhookError,
    WebhookSignatureError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/github", status_code=status.HTTP_202_ACCEPTED)
async def github_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_github_event: str = Header(..., alias="X-GitHub-Event"),
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    x_github_delivery: str = Header(..., alias="X-GitHub-Delivery"),
):
    """
    Handle GitHub webhook events.

    This endpoint receives webhook events from GitHub when repository
    events occur (push, pull_request, issues, etc.).

    GitHub will send:
    - X-GitHub-Event: Event type (push, pull_request, etc.)
    - X-Hub-Signature-256: HMAC-SHA256 signature of the payload
    - X-GitHub-Delivery: Unique delivery ID
    """
    # Get raw body for signature verification
    body = await request.body()

    webhook_service = WebhookService(db)

    # Verify webhook signature
    try:
        webhook_service.verify_signature(
            payload=body,
            signature=x_hub_signature_256,
        )
    except WebhookSignatureError as e:
        logger.warning(f"Webhook signature verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    # Parse JSON payload
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    # Process webhook event
    try:
        webhook_event = await webhook_service.process_webhook(
            event_type=x_github_event,
            delivery_id=x_github_delivery,
            payload=payload,
        )
        await db.commit()

        logger.info(
            f"Processed GitHub webhook: {x_github_event} "
            f"(delivery: {x_github_delivery})"
        )

        return {
            "message": "Webhook received",
            "event_id": webhook_event.id,
            "event_type": x_github_event,
            "processed": webhook_event.processed,
        }

    except WebhookError as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/github/events", response_model=List[WebhookEventResponse])
async def list_webhook_events(
    repository_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    processed: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List received webhook events.

    Can be filtered by repository, event type, or processing status.
    Requires authentication. Non-admin users must scope the listing to a
    repository they have access to.
    """
    from sqlalchemy import select
    from app.models.github import GitHubRepository
    from app.models.project import Project
    from app.models.team import TeamMember

    # Non-admins may only list events for a repository they can access.
    if not current_user.is_admin:
        if not repository_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="A repository_id you have access to is required",
            )

        repo_result = await db.execute(
            select(GitHubRepository).where(GitHubRepository.id == repository_id)
        )
        github_repo = repo_result.scalar_one_or_none()
        if not github_repo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repository not found",
            )

        project_result = await db.execute(
            select(Project).where(Project.id == github_repo.project_id)
        )
        project = project_result.scalar_one_or_none()

        authorized = bool(project and project.is_public)
        if not authorized and project and project.team_id:
            member_result = await db.execute(
                select(TeamMember).where(
                    TeamMember.team_id == project.team_id,
                    TeamMember.user_id == current_user.id,
                    TeamMember.is_active == True,
                )
            )
            authorized = member_result.scalar_one_or_none() is not None

        if not authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this repository",
            )

    webhook_service = WebhookService(db)

    events = await webhook_service.get_webhook_events(
        repository_id=repository_id,
        event_type=event_type,
        processed=processed,
        limit=limit,
    )

    return [
        WebhookEventResponse(
            id=e.id,
            repository_id=e.repository_id,
            event_type=e.event_type,
            action=e.action,
            delivery_id=e.delivery_id,
            processed=e.processed,
            processed_at=e.processed_at,
            processing_error=e.processing_error,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )
        for e in events
    ]


@router.get("/github/events/{event_id}", response_model=WebhookEventResponse)
async def get_webhook_event(
    event_id: str,
    include_payload: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific webhook event.

    Optionally include the full payload.
    """
    from sqlalchemy import select
    from app.models.github import WebhookEvent, GitHubRepository
    from app.models.project import Project
    from app.models.team import TeamMember

    result = await db.execute(
        select(WebhookEvent).where(WebhookEvent.id == event_id)
    )
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook event not found",
        )

    # Authorize: scope the event (and its raw payload) to users who can access
    # the underlying repository's project. Events not tied to a repository are
    # restricted to admins since they cannot be scoped to a team.
    authorized = current_user.is_admin
    if not authorized and event.repository_id:
        repo_result = await db.execute(
            select(GitHubRepository).where(GitHubRepository.id == event.repository_id)
        )
        github_repo = repo_result.scalar_one_or_none()
        if github_repo:
            project_result = await db.execute(
                select(Project).where(Project.id == github_repo.project_id)
            )
            project = project_result.scalar_one_or_none()
            if project and project.is_public:
                authorized = True
            elif project and project.team_id:
                member_result = await db.execute(
                    select(TeamMember).where(
                        TeamMember.team_id == project.team_id,
                        TeamMember.user_id == current_user.id,
                        TeamMember.is_active == True,
                    )
                )
                authorized = member_result.scalar_one_or_none() is not None

    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this webhook event",
        )

    response = WebhookEventResponse(
        id=event.id,
        repository_id=event.repository_id,
        event_type=event.event_type,
        action=event.action,
        delivery_id=event.delivery_id,
        processed=event.processed,
        processed_at=event.processed_at,
        processing_error=event.processing_error,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )

    # Include payload if requested
    if include_payload:
        response_dict = response.model_dump()
        response_dict["payload"] = event.payload
        return response_dict

    return response
