"""
GitHub integration models
"""
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import GUID, JSONBType, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project


class GitHubConnectionStatus(str, Enum):
    """GitHub connection status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class SyncStatus(str, Enum):
    """Sync operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class WebhookEventType(str, Enum):
    """GitHub webhook event types"""
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    ISSUES = "issues"
    ISSUE_COMMENT = "issue_comment"
    CREATE = "create"
    DELETE = "delete"
    RELEASE = "release"
    WORKFLOW_RUN = "workflow_run"


class GitHubConnection(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    GitHub OAuth connection for a user.
    Stores encrypted access tokens.
    """
    __tablename__ = "github_connections"

    # User relationship
    user_id: Mapped[str] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # GitHub user info
    github_user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    github_username: Mapped[str] = mapped_column(String(255), nullable=False)
    github_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    github_avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # OAuth tokens (encrypted)
    access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Token metadata
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    scopes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Comma-separated

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default=GitHubConnectionStatus.ACTIVE.value,
        nullable=False
    )

    # Last used
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", backref="github_connection")

    __table_args__ = (
        Index("ix_github_connections_user_status", "user_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<GitHubConnection user={self.user_id} github={self.github_username}>"


class GitHubRepository(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    GitHub repository linked to a project.
    Stores repository metadata and sync settings.
    """
    __tablename__ = "github_repositories"

    # Project relationship
    project_id: Mapped[str] = mapped_column(
        GUID,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # Repository info
    github_repo_id: Mapped[str] = mapped_column(String(50), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(510), nullable=False)  # owner/name
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    html_url: Mapped[str] = mapped_column(Text, nullable=False)
    clone_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ssh_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Repository metadata
    default_branch: Mapped[str] = mapped_column(String(255), default="main", nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_fork: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    topics: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array as string

    # Stats (cached from GitHub)
    stars_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    forks_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    watchers_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    open_issues_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Sync settings
    sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sync_commits: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sync_issues: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sync_prs: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Sync state
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    last_sync_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    last_sync_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_commit_sha: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)

    # Webhook
    webhook_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    webhook_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", backref="github_repository")

    __table_args__ = (
        Index("ix_github_repositories_owner_name", "owner", "name"),
    )

    def __repr__(self) -> str:
        return f"<GitHubRepository {self.full_name}>"


class SyncHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    History of sync operations for a repository.
    """
    __tablename__ = "sync_history"

    # Repository relationship
    repository_id: Mapped[str] = mapped_column(
        GUID,
        ForeignKey("github_repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Sync info
    sync_type: Mapped[str] = mapped_column(String(50), nullable=False)  # manual, webhook, scheduled
    status: Mapped[str] = mapped_column(
        String(20),
        default=SyncStatus.PENDING.value,
        nullable=False
    )

    # Progress
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Results
    commits_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    issues_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    prs_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON

    # Relationships
    repository: Mapped["GitHubRepository"] = relationship(
        "GitHubRepository",
        backref="sync_history"
    )

    def __repr__(self) -> str:
        return f"<SyncHistory {self.repository_id} {self.status}>"


class WebhookEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Received webhook events from GitHub.
    """
    __tablename__ = "webhook_events"

    # Repository (optional - might be org-level webhook)
    repository_id: Mapped[Optional[str]] = mapped_column(
        GUID,
        ForeignKey("github_repositories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Event info
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    delivery_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Payload
    payload: Mapped[Optional[dict]] = mapped_column(JSONBType, nullable=True)

    # Processing
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    repository: Mapped[Optional["GitHubRepository"]] = relationship(
        "GitHubRepository",
        backref="webhook_events"
    )

    __table_args__ = (
        Index("ix_webhook_events_type_processed", "event_type", "processed"),
    )

    def __repr__(self) -> str:
        return f"<WebhookEvent {self.event_type} {self.delivery_id}>"
