"""
GitHub Webhook handler service
"""
import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.github import (
    GitHubRepository,
    WebhookEvent,
    WebhookEventType,
    SyncHistory,
    SyncStatus,
)
from app.models.commit import Commit
from app.models.project import Project

logger = logging.getLogger(__name__)


class WebhookError(Exception):
    """Webhook processing error"""
    pass


class WebhookSignatureError(WebhookError):
    """Webhook signature verification failed"""
    pass


class WebhookService:
    """
    Service for handling GitHub webhooks.
    Verifies signatures and processes webhook events.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    def verify_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str = None,
    ) -> bool:
        """
        Verify GitHub webhook signature.

        Args:
            payload: Raw request body
            signature: X-Hub-Signature-256 header value
            secret: Webhook secret (uses settings if not provided)

        Returns:
            True if signature is valid

        Raises:
            WebhookSignatureError: If signature is invalid
        """
        secret = secret or settings.GITHUB_WEBHOOK_SECRET
        if not secret:
            logger.warning("No webhook secret configured, skipping signature verification")
            return True

        if not signature:
            raise WebhookSignatureError("Missing signature header")

        # Signature format: sha256=<hash>
        if not signature.startswith("sha256="):
            raise WebhookSignatureError("Invalid signature format")

        expected_signature = signature[7:]  # Remove "sha256=" prefix

        # Compute HMAC-SHA256
        computed_hash = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(computed_hash, expected_signature):
            raise WebhookSignatureError("Signature verification failed")

        return True

    async def process_webhook(
        self,
        event_type: str,
        delivery_id: str,
        payload: Dict[str, Any],
    ) -> WebhookEvent:
        """
        Process a webhook event.

        Args:
            event_type: GitHub event type (push, pull_request, etc.)
            delivery_id: Unique delivery ID
            payload: Event payload

        Returns:
            Created WebhookEvent record
        """
        # Get repository info from payload
        repository_id = None
        repo_info = payload.get("repository", {})
        if repo_info:
            github_repo_id = str(repo_info.get("id", ""))
            if github_repo_id:
                result = await self.db.execute(
                    select(GitHubRepository).where(
                        GitHubRepository.github_repo_id == github_repo_id
                    )
                )
                github_repo = result.scalar_one_or_none()
                if github_repo:
                    repository_id = github_repo.id

        # Create webhook event record
        action = payload.get("action")
        webhook_event = WebhookEvent(
            id=str(uuid4()),
            repository_id=repository_id,
            event_type=event_type,
            action=action,
            delivery_id=delivery_id,
            payload=payload,
            processed=False,
        )
        self.db.add(webhook_event)
        await self.db.flush()

        # Process event based on type
        try:
            if event_type == "push":
                await self._handle_push_event(webhook_event, payload)
            elif event_type == "pull_request":
                await self._handle_pull_request_event(webhook_event, payload)
            elif event_type == "issues":
                await self._handle_issues_event(webhook_event, payload)
            elif event_type == "create":
                await self._handle_create_event(webhook_event, payload)
            elif event_type == "delete":
                await self._handle_delete_event(webhook_event, payload)
            elif event_type == "release":
                await self._handle_release_event(webhook_event, payload)
            elif event_type == "ping":
                await self._handle_ping_event(webhook_event, payload)
            else:
                logger.info(f"Unhandled webhook event type: {event_type}")

            webhook_event.processed = True
            webhook_event.processed_at = datetime.now(timezone.utc)

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            webhook_event.processing_error = str(e)

        await self.db.flush()
        await self.db.refresh(webhook_event)

        return webhook_event

    async def _handle_push_event(
        self,
        webhook_event: WebhookEvent,
        payload: Dict[str, Any],
    ) -> None:
        """
        Handle push event - sync new commits.

        Push events contain:
        - ref: Branch reference (refs/heads/main)
        - before: SHA before the push
        - after: SHA after the push
        - commits: Array of commit objects
        """
        if not webhook_event.repository_id:
            logger.warning("Push event for unknown repository")
            return

        # Get GitHub repository
        result = await self.db.execute(
            select(GitHubRepository).where(
                GitHubRepository.id == webhook_event.repository_id
            )
        )
        github_repo = result.scalar_one_or_none()
        if not github_repo or not github_repo.sync_enabled:
            return

        commits_data = payload.get("commits", [])
        if not commits_data:
            return

        # Get existing commit SHAs
        result = await self.db.execute(
            select(Commit.sha).where(Commit.project_id == github_repo.project_id)
        )
        existing_shas = {row[0] for row in result.fetchall()}

        # Process commits
        new_commits = []
        for commit_data in commits_data:
            sha = commit_data.get("id")
            if sha in existing_shas:
                continue

            message = commit_data.get("message", "")
            commit_type = self._parse_commit_type(message)

            author_info = commit_data.get("author", {})
            timestamp_str = commit_data.get("timestamp", "")

            # Parse timestamp
            try:
                commit_date = datetime.fromisoformat(
                    timestamp_str.replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                commit_date = datetime.now(timezone.utc)

            new_commit = Commit(
                id=str(uuid4()),
                project_id=github_repo.project_id,
                sha=sha,
                message=message,
                author=author_info.get("name", "Unknown"),
                author_email=author_info.get("email", ""),
                commit_date=commit_date,
                commit_type=commit_type,
                files_changed=len(commit_data.get("added", [])) +
                              len(commit_data.get("modified", [])) +
                              len(commit_data.get("removed", [])),
                url=commit_data.get("url", ""),
            )
            new_commits.append(new_commit)

        if new_commits:
            self.db.add_all(new_commits)

            # Update repository last commit SHA
            github_repo.last_commit_sha = payload.get("after")
            github_repo.last_sync_at = datetime.now(timezone.utc)

            # Update project stats
            result = await self.db.execute(
                select(Project).where(Project.id == github_repo.project_id)
            )
            project = result.scalar_one_or_none()
            if project:
                project.total_commits = (project.total_commits or 0) + len(new_commits)
                project.last_synced_at = datetime.now(timezone.utc)

            logger.info(
                f"Processed {len(new_commits)} commits from push event "
                f"for {github_repo.full_name}"
            )

    async def _handle_pull_request_event(
        self,
        webhook_event: WebhookEvent,
        payload: Dict[str, Any],
    ) -> None:
        """
        Handle pull request event.

        Actions: opened, closed, reopened, edited, synchronize, etc.
        """
        action = payload.get("action")
        pr = payload.get("pull_request", {})

        logger.info(
            f"Pull request #{pr.get('number')} {action}: {pr.get('title')}"
        )

        # TODO: Implement PR tracking when PullRequest model is available

    async def _handle_issues_event(
        self,
        webhook_event: WebhookEvent,
        payload: Dict[str, Any],
    ) -> None:
        """
        Handle issues event.

        Actions: opened, closed, reopened, edited, labeled, etc.
        """
        action = payload.get("action")
        issue = payload.get("issue", {})

        logger.info(
            f"Issue #{issue.get('number')} {action}: {issue.get('title')}"
        )

        # TODO: Implement issue tracking when Issue model is available

    async def _handle_create_event(
        self,
        webhook_event: WebhookEvent,
        payload: Dict[str, Any],
    ) -> None:
        """Handle create event (branch or tag creation)"""
        ref_type = payload.get("ref_type")  # branch, tag
        ref = payload.get("ref")  # branch/tag name

        logger.info(f"Created {ref_type}: {ref}")

    async def _handle_delete_event(
        self,
        webhook_event: WebhookEvent,
        payload: Dict[str, Any],
    ) -> None:
        """Handle delete event (branch or tag deletion)"""
        ref_type = payload.get("ref_type")
        ref = payload.get("ref")

        logger.info(f"Deleted {ref_type}: {ref}")

    async def _handle_release_event(
        self,
        webhook_event: WebhookEvent,
        payload: Dict[str, Any],
    ) -> None:
        """Handle release event"""
        action = payload.get("action")
        release = payload.get("release", {})

        logger.info(
            f"Release {action}: {release.get('tag_name')} - {release.get('name')}"
        )

    async def _handle_ping_event(
        self,
        webhook_event: WebhookEvent,
        payload: Dict[str, Any],
    ) -> None:
        """Handle ping event (webhook setup confirmation)"""
        zen = payload.get("zen", "")
        hook_id = payload.get("hook_id")

        logger.info(f"Ping received for hook {hook_id}: {zen}")

    def _parse_commit_type(self, message: str) -> str:
        """Parse commit type from conventional commit message"""
        if not message:
            return "chore"

        subject = message.split("\n")[0].lower()

        if subject.startswith("feat"):
            return "feat"
        elif subject.startswith("fix"):
            return "fix"
        elif subject.startswith("docs"):
            return "docs"
        elif subject.startswith("refactor"):
            return "refactor"
        elif subject.startswith("test"):
            return "test"
        elif subject.startswith("perf"):
            return "perf"
        elif subject.startswith("style"):
            return "style"
        elif subject.startswith("chore"):
            return "chore"
        elif subject.startswith("ci"):
            return "ci"
        elif subject.startswith("build"):
            return "build"

        return "chore"

    async def get_webhook_events(
        self,
        repository_id: str = None,
        event_type: str = None,
        processed: bool = None,
        limit: int = 50,
    ) -> list[WebhookEvent]:
        """
        Get webhook events with optional filters.

        Args:
            repository_id: Filter by repository
            event_type: Filter by event type
            processed: Filter by processed status
            limit: Maximum records

        Returns:
            List of WebhookEvent records
        """
        query = select(WebhookEvent)

        if repository_id:
            query = query.where(WebhookEvent.repository_id == repository_id)
        if event_type:
            query = query.where(WebhookEvent.event_type == event_type)
        if processed is not None:
            query = query.where(WebhookEvent.processed == processed)

        query = query.order_by(WebhookEvent.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())
