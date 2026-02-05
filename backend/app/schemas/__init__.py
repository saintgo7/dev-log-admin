"""
Pydantic Schemas for API request/response validation
"""
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserInDB,
)
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamMemberCreate,
    TeamMemberResponse,
)
from app.schemas.auth import (
    Token,
    TokenPayload,
    LoginRequest,
    RegisterRequest,
    OAuthCallback,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)
from app.schemas.commit import (
    CommitCreate,
    CommitResponse,
)
from app.schemas.github import (
    GitHubOAuthRequest,
    GitHubOAuthResponse,
    GitHubOAuthCallback,
    GitHubConnectionCreate,
    GitHubConnectionResponse,
    GitHubConnectionStatus,
    GitHubRepositoryCreate,
    GitHubRepositoryUpdate,
    GitHubRepositoryResponse,
    SyncRequest,
    SyncHistoryResponse,
    SyncStatusResponse,
    WebhookSetupRequest,
    WebhookSetupResponse,
    WebhookEventResponse,
    GitHubRateLimitInfo,
)

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse", "UserInDB",
    "TeamCreate", "TeamUpdate", "TeamResponse", "TeamMemberCreate", "TeamMemberResponse",
    "Token", "TokenPayload", "LoginRequest", "RegisterRequest", "OAuthCallback",
    "ProjectCreate", "ProjectUpdate", "ProjectResponse",
    "CommitCreate", "CommitResponse",
    # GitHub
    "GitHubOAuthRequest", "GitHubOAuthResponse", "GitHubOAuthCallback",
    "GitHubConnectionCreate", "GitHubConnectionResponse", "GitHubConnectionStatus",
    "GitHubRepositoryCreate", "GitHubRepositoryUpdate", "GitHubRepositoryResponse",
    "SyncRequest", "SyncHistoryResponse", "SyncStatusResponse",
    "WebhookSetupRequest", "WebhookSetupResponse", "WebhookEventResponse",
    "GitHubRateLimitInfo",
]
