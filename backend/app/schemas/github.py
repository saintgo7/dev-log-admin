"""
GitHub integration schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

from app.schemas.base import BaseSchema, TimestampMixin


# ============================================================================
# GitHub OAuth
# ============================================================================

class GitHubOAuthRequest(BaseModel):
    """Request to initiate GitHub OAuth"""
    redirect_uri: Optional[str] = None
    scopes: Optional[List[str]] = Field(
        default=["repo", "read:user", "user:email"],
        description="OAuth scopes to request"
    )


class GitHubOAuthResponse(BaseModel):
    """OAuth authorization URL response"""
    authorization_url: str
    state: str


class GitHubOAuthCallback(BaseModel):
    """GitHub OAuth callback data"""
    code: str
    state: str


class GitHubConnectionCreate(BaseModel):
    """Create GitHub connection from OAuth callback"""
    code: str
    state: str


class GitHubConnectionResponse(BaseSchema, TimestampMixin):
    """GitHub connection response"""
    id: str
    user_id: str
    github_user_id: str
    github_username: str
    github_email: Optional[str] = None
    github_avatar_url: Optional[str] = None
    status: str
    scopes: Optional[str] = None
    last_used_at: Optional[datetime] = None


class GitHubConnectionStatus(BaseModel):
    """GitHub connection status check"""
    connected: bool
    connection: Optional[GitHubConnectionResponse] = None


# ============================================================================
# GitHub Repository
# ============================================================================

class GitHubRepositoryBase(BaseModel):
    """Base GitHub repository data"""
    owner: str
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    default_branch: str = "main"
    is_private: bool = False
    is_fork: bool = False
    language: Optional[str] = None


class GitHubRepositoryCreate(BaseModel):
    """Link a GitHub repository to a project"""
    project_id: str
    owner: str
    name: str


class GitHubRepositoryUpdate(BaseModel):
    """Update repository sync settings"""
    sync_enabled: Optional[bool] = None
    sync_commits: Optional[bool] = None
    sync_issues: Optional[bool] = None
    sync_prs: Optional[bool] = None


class GitHubRepositoryResponse(GitHubRepositoryBase, TimestampMixin):
    """GitHub repository response"""
    id: str
    project_id: str
    github_repo_id: str
    clone_url: Optional[str] = None
    ssh_url: Optional[str] = None
    topics: Optional[str] = None

    # Stats
    stars_count: int = 0
    forks_count: int = 0
    watchers_count: int = 0
    open_issues_count: int = 0

    # Sync settings
    sync_enabled: bool = True
    sync_commits: bool = True
    sync_issues: bool = False
    sync_prs: bool = False

    # Sync state
    last_sync_at: Optional[datetime] = None
    last_sync_status: Optional[str] = None
    last_sync_error: Optional[str] = None
    last_commit_sha: Optional[str] = None

    # Webhook
    webhook_active: bool = False


class GitHubRepositoryList(BaseModel):
    """List of GitHub repositories from API"""
    repositories: List[GitHubRepositoryBase]
    total_count: int


# ============================================================================
# Sync Operations
# ============================================================================

class SyncRequest(BaseModel):
    """Manual sync request"""
    sync_commits: bool = True
    sync_issues: bool = False
    sync_prs: bool = False
    full_sync: bool = False  # If true, sync all history, not just new


class SyncHistoryResponse(BaseSchema, TimestampMixin):
    """Sync history entry"""
    id: str
    repository_id: str
    sync_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    commits_synced: int = 0
    issues_synced: int = 0
    prs_synced: int = 0
    error_message: Optional[str] = None


class SyncStatusResponse(BaseModel):
    """Current sync status"""
    repository_id: str
    is_syncing: bool
    last_sync: Optional[SyncHistoryResponse] = None
    pending_syncs: int = 0


# ============================================================================
# GitHub API Data
# ============================================================================

class GitHubUserInfo(BaseModel):
    """GitHub user info from API"""
    id: int
    login: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    html_url: str
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    public_repos: int = 0
    public_gists: int = 0
    followers: int = 0
    following: int = 0


class GitHubCommitInfo(BaseModel):
    """GitHub commit info"""
    sha: str
    message: str
    author_name: str
    author_email: str
    author_date: datetime
    committer_name: Optional[str] = None
    committer_email: Optional[str] = None
    committer_date: Optional[datetime] = None
    url: str
    additions: int = 0
    deletions: int = 0
    files_changed: int = 0


class GitHubBranchInfo(BaseModel):
    """GitHub branch info"""
    name: str
    sha: str
    protected: bool = False


class GitHubPullRequestInfo(BaseModel):
    """GitHub PR info"""
    number: int
    title: str
    state: str  # open, closed
    body: Optional[str] = None
    user_login: str
    head_ref: str
    base_ref: str
    created_at: datetime
    updated_at: datetime
    merged_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    html_url: str


class GitHubIssueInfo(BaseModel):
    """GitHub issue info"""
    number: int
    title: str
    state: str  # open, closed
    body: Optional[str] = None
    user_login: str
    labels: List[str] = []
    assignees: List[str] = []
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    html_url: str


# ============================================================================
# Webhook
# ============================================================================

class WebhookSetupRequest(BaseModel):
    """Request to setup webhook for a repository"""
    repository_id: str
    events: List[str] = Field(
        default=["push", "pull_request", "issues"],
        description="Events to subscribe to"
    )


class WebhookSetupResponse(BaseModel):
    """Webhook setup response"""
    webhook_id: str
    active: bool
    events: List[str]
    url: str


class WebhookEventResponse(BaseSchema, TimestampMixin):
    """Webhook event record"""
    id: str
    repository_id: Optional[str] = None
    event_type: str
    action: Optional[str] = None
    delivery_id: str
    processed: bool
    processed_at: Optional[datetime] = None
    processing_error: Optional[str] = None


# ============================================================================
# Rate Limit
# ============================================================================

class GitHubRateLimitInfo(BaseModel):
    """GitHub API rate limit info"""
    limit: int
    remaining: int
    reset_at: datetime
    used: int
