# Graph Report - .  (2026-06-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1436 nodes · 2877 edges · 103 communities (81 shown, 22 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 677 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0da06c31`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Webhook Handling|Webhook Handling]]
- [[_COMMUNITY_Database Models|Database Models]]
- [[_COMMUNITY_Team Management|Team Management]]
- [[_COMMUNITY_GitHub API Tests|GitHub API Tests]]
- [[_COMMUNITY_Application Setup|Application Setup]]
- [[_COMMUNITY_GitHub Client|GitHub Client]]
- [[_COMMUNITY_Team Endpoints Tests|Team Endpoints Tests]]
- [[_COMMUNITY_UI Components|UI Components]]
- [[_COMMUNITY_Authentication Services|Authentication Services]]
- [[_COMMUNITY_GitHub API Errors|GitHub API Errors]]
- [[_COMMUNITY_Auth Endpoints Tests|Auth Endpoints Tests]]
- [[_COMMUNITY_GitHub Schemas|GitHub Schemas]]
- [[_COMMUNITY_Development Guidelines|Development Guidelines]]
- [[_COMMUNITY_Database Migration|Database Migration]]
- [[_COMMUNITY_Sync Service|Sync Service]]
- [[_COMMUNITY_Dashboard UI|Dashboard UI]]
- [[_COMMUNITY_Commit Model|Commit Model]]
- [[_COMMUNITY_Security Utilities|Security Utilities]]
- [[_COMMUNITY_Project Hooks|Project Hooks]]
- [[_COMMUNITY_Team Endpoints|Team Endpoints]]
- [[_COMMUNITY_Team Service|Team Service]]
- [[_COMMUNITY_Auth Service|Auth Service]]
- [[_COMMUNITY_User Authentication|User Authentication]]
- [[_COMMUNITY_GitHub OAuth Service|GitHub OAuth Service]]
- [[_COMMUNITY_API Responses|API Responses]]
- [[_COMMUNITY_Test Configuration|Test Configuration]]
- [[_COMMUNITY_UI Layout|UI Layout]]
- [[_COMMUNITY_User Service|User Service]]
- [[_COMMUNITY_Token Encryption|Token Encryption]]
- [[_COMMUNITY_Analytics Page|Analytics Page]]
- [[_COMMUNITY_Token Verification|Token Verification]]
- [[_COMMUNITY_Frontend Configuration|Frontend Configuration]]
- [[_COMMUNITY_TypeScript Config|TypeScript Config]]
- [[_COMMUNITY_Legacy API|Legacy API]]
- [[_COMMUNITY_Auth Schemas|Auth Schemas]]
- [[_COMMUNITY_Frontend Setup|Frontend Setup]]
- [[_COMMUNITY_User Management|User Management]]
- [[_COMMUNITY_Team Schemas|Team Schemas]]
- [[_COMMUNITY_Project Analysis|Project Analysis]]
- [[_COMMUNITY_Frontend Dependencies|Frontend Dependencies]]
- [[_COMMUNITY_Project Discovery|Project Discovery]]
- [[_COMMUNITY_Project Schemas|Project Schemas]]
- [[_COMMUNITY_Database Migrations|Database Migrations]]
- [[_COMMUNITY_Commit Schemas|Commit Schemas]]
- [[_COMMUNITY_User Schemas|User Schemas]]
- [[_COMMUNITY_UI Elements|UI Elements]]
- [[_COMMUNITY_Dev Dependencies|Dev Dependencies]]
- [[_COMMUNITY_Project Frontend|Project Frontend]]
- [[_COMMUNITY_Git Log Processing|Git Log Processing]]
- [[_COMMUNITY_Package Config|Package Config]]
- [[_COMMUNITY_Pagination|Pagination]]
- [[_COMMUNITY_GitHub Client|GitHub Client]]
- [[_COMMUNITY_App Configuration|App Configuration]]
- [[_COMMUNITY_App Layout|App Layout]]
- [[_COMMUNITY_JSON Generation|JSON Generation]]
- [[_COMMUNITY_App Constants|App Constants]]
- [[_COMMUNITY_Dashboard Scripts|Dashboard Scripts]]
- [[_COMMUNITY_Base Model|Base Model]]
- [[_COMMUNITY_Sync Script|Sync Script]]
- [[_COMMUNITY_Start Scripts|Start Scripts]]
- [[_COMMUNITY_Token Management|Token Management]]
- [[_COMMUNITY_Access Control|Access Control]]
- [[_COMMUNITY_HTML Generation|HTML Generation]]
- [[_COMMUNITY_Script Installation|Script Installation]]
- [[_COMMUNITY_Database Setup|Database Setup]]
- [[_COMMUNITY_Legacy Pages|Legacy Pages]]
- [[_COMMUNITY_Status Script|Status Script]]
- [[_COMMUNITY_Stop Script|Stop Script]]
- [[_COMMUNITY_Signature Testing|Signature Testing]]
- [[_COMMUNITY_Phase 2 Init|Phase 2 Init]]
- [[_COMMUNITY_Project Info|Project Info]]
- [[_COMMUNITY_ESLint Config|ESLint Config]]
- [[_COMMUNITY_Next Config|Next Config]]
- [[_COMMUNITY_PostCSS Config|PostCSS Config]]
- [[_COMMUNITY_Ownership Check|Ownership Check]]
- [[_COMMUNITY_Admin Check|Admin Check]]
- [[_COMMUNITY_Schemas Init|Schemas Init]]
- [[_COMMUNITY_Migration Script|Migration Script]]
- [[_COMMUNITY_Sync Legacy Script|Sync Legacy Script]]
- [[_COMMUNITY_Mock Response|Mock Response]]
- [[_COMMUNITY_Test Client|Test Client]]
- [[_COMMUNITY_OAuth Scopes Test|OAuth Scopes Test]]
- [[_COMMUNITY_Schema Validation|Schema Validation]]
- [[_COMMUNITY_Sync Defaults Test|Sync Defaults Test]]
- [[_COMMUNITY_Signature Missing Test|Signature Missing Test]]
- [[_COMMUNITY_Signature Format Test|Signature Format Test]]

## God Nodes (most connected - your core abstractions)
1. `User` - 79 edges
2. `cn()` - 66 edges
3. `Project` - 54 edges
4. `TeamMember` - 43 edges
5. `TeamService` - 43 edges
6. `GitHubClient` - 39 edges
7. `WebhookService` - 38 edges
8. `Dev Log #004: Multi-Agent Parallel Development` - 38 edges
9. `CurrentUser` - 34 edges
10. `GitHubOAuthService` - 32 edges

## Surprising Connections (you probably didn't know these)
- `analyze_git_repo()` --calls--> `timedelta`  [INFERRED]
  tools/deep-analyze.py → backend/app/core/security.py
- `Connection` --uses--> `Base`  [INFERRED]
  backend/migrations/env.py → backend/app/db/session.py
- `AsyncSession` --uses--> `User`  [INFERRED]
  backend/app/services/github_oauth_service.py → backend/app/models/user.py
- `User` --uses--> `User`  [INFERRED]
  backend/app/services/github_oauth_service.py → backend/app/models/user.py
- `AsyncSession` --uses--> `User`  [INFERRED]
  backend/app/services/user_service.py → backend/app/models/user.py

## Import Cycles
- 1-file cycle: `backend/app/main.py -> backend/app/main.py`
- 1-file cycle: `backend/app/core/security.py -> backend/app/core/security.py`
- 1-file cycle: `backend/app/models/base.py -> backend/app/models/base.py`
- 1-file cycle: `backend/scripts/migrate_sqlite_to_postgres.py -> backend/scripts/migrate_sqlite_to_postgres.py`
- 1-file cycle: `backend/app/services/github_oauth_service.py -> backend/app/services/github_oauth_service.py`
- 1-file cycle: `backend/app/services/github_client_service.py -> backend/app/services/github_client_service.py`

## Communities (103 total, 22 thin omitted)

### Community 0 - "Webhook Handling"
Cohesion: 0.06
Nodes (36): AsyncSession, User, Any, Request, WebhookEventResponse, GitHub Webhook handler service, Process a webhook event.          Args:             event_type: GitHub event typ, Handle push event - sync new commits.          Push events contain:         - re (+28 more)

### Community 1 - "Database Models"
Cohesion: 0.11
Nodes (34): Base, Base class for SQLAlchemy models, DeclarativeBase, Enum, Mixin for created_at and updated_at timestamps, Mixin for UUID primary key, TimestampMixin, UUIDPrimaryKeyMixin (+26 more)

### Community 2 - "Team Management"
Cohesion: 0.16
Nodes (37): Depends, Path, Project, Team, TeamMember, User, AsyncSession, TeamCreate (+29 more)

### Community 3 - "GitHub API Tests"
Cohesion: 0.06
Nodes (27): AsyncClient, AsyncSession, Integration tests for GitHub API endpoints, Test getting non-existent repository, Test GitHub sync endpoints, Test syncing non-existent repository, Test GitHub OAuth endpoints, Test getting sync status for non-existent repository (+19 more)

### Community 4 - "Application Setup"
Cohesion: 0.06
Nodes (37): create_application(), lifespan(), Dev Log Admin API - Main Application  FastAPI application with: - v1 API: Legacy, Application lifespan manager, Create and configure FastAPI application, AsyncSession, close_db(), get_async_database_url() (+29 more)

### Community 5 - "GitHub Client"
Cohesion: 0.07
Nodes (23): Any, GitHubBranchInfo, GitHubCommitInfo, GitHubIssueInfo, GitHubPullRequestInfo, GitHubRateLimitInfo, GitHubUserInfo, GitHubClient (+15 more)

### Community 6 - "Team Endpoints Tests"
Cohesion: 0.07
Nodes (25): AsyncClient, Integration tests for team endpoints, Tests for POST /api/v2/teams endpoint, Should return team details, Should reject non-member access, Should create team successfully, Should return 404 for nonexistent team, Tests for PATCH /api/v2/teams/{team_id} endpoint (+17 more)

### Community 7 - "UI Components"
Cohesion: 0.09
Nodes (28): MobileSidebar(), navItems, SidebarProps, cn(), Avatar(), AvatarBadge(), AvatarFallback(), AvatarGroup() (+20 more)

### Community 8 - "Authentication Services"
Cohesion: 0.05
Nodes (38): Authentication Endpoints, Authentication Service, GitHub Client Service, GitHub Connection Model, GitHub OAuth Service, GitHub Repository Model, Initial Database Migration, Row Level Security Migration (+30 more)

### Community 9 - "GitHub API Errors"
Cohesion: 0.19
Nodes (33): AsyncSession, User, Exception, GitHubOAuthCallback, GitHubOAuthRequest, GitHubRepositoryCreate, GitHubRepositoryUpdate, GitHubAPIError (+25 more)

### Community 10 - "Auth Endpoints Tests"
Cohesion: 0.08
Nodes (22): AsyncClient, Integration tests for authentication endpoints, Tests for /api/v2/auth/register endpoint, Should reject nonexistent email, Tests for /api/v2/auth/me endpoint, Should return current user info, Should reject unauthenticated request, Should register new user successfully (+14 more)

### Community 11 - "GitHub Schemas"
Cohesion: 0.09
Nodes (34): BaseModel, GitHubBranchInfo, GitHubCommitInfo, GitHubConnectionCreate, GitHubConnectionStatus, GitHubIssueInfo, GitHubOAuthCallback, GitHubOAuthRequest (+26 more)

### Community 12 - "Development Guidelines"
Cohesion: 0.06
Nodes (34): Backend README, Backend Requirements, Branch Strategy, Coding Conventions, Commands, Environment Variables, Port Assignment, Prohibited (+26 more)

### Community 13 - "Database Migration"
Cohesion: 0.10
Nodes (19): Any, datetime, Path, main(), MigrationError, PostgresMigrator, Create default admin user and return ID, Create default team and return ID (+11 more)

### Community 14 - "Sync Service"
Cohesion: 0.09
Nodes (21): GitHubClient, GitHubRepository, Repository synchronization service, Unlink a GitHub repository from a project.          Args:             project_id, List available GitHub repositories for linking.          Args:             user_, Synchronize a GitHub repository.          Args:             user_id: User ID (fo, Update repository metadata from GitHub API response, Sync commits from GitHub to local database.          Returns:             Number (+13 more)

### Community 15 - "Dashboard UI"
Cohesion: 0.17
Nodes (20): COLORS, ChartDataPoint, CommitChartProps, RecentActivityProps, StatsCardProps, StatsCardsProps, themes, RecentActivity (+12 more)

### Community 16 - "Commit Model"
Cohesion: 0.14
Nodes (28): AsyncSession, CurrentUser, Depends, get_db, Project, AsyncSession, CurrentUserOptional, Commit (+20 more)

### Community 17 - "Security Utilities"
Cohesion: 0.10
Nodes (21): Any, create_access_token(), create_refresh_token(), decode_token(), Security utilities - JWT, password hashing, OAuth, Decode and validate a JWT token      Args:         token: JWT token string, Create a JWT access token      Args:         subject: User ID or other identifie, Create a JWT refresh token with longer expiration      Args:         subject: Us (+13 more)

### Community 18 - "Project Hooks"
Cohesion: 0.09
Nodes (25): ProjectCardProps, useProject(), useProjectCommits(), UseProjectCommitsParams, UseProjectCommitsReturn, UseProjectReturn, UseProjectsReturn, UseOverviewStatsReturn (+17 more)

### Community 19 - "Team Endpoints"
Cohesion: 0.15
Nodes (28): AsyncSession, CurrentUser, Depends, get_db, TeamCreate, TeamUpdate, TeamMemberCreate, TeamMemberUpdate (+20 more)

### Community 20 - "Team Service"
Cohesion: 0.12
Nodes (16): Team, TeamMember, User, Delete a team          Args:             team: Team to delete, Get all teams the user is a member of          Args:             user: User, Get all members of a team          Args:             team: Team          Returns, Add a member to team          Args:             team: Team             user: Use, Update member role          Args:             team: Team             user_id: Us (+8 more)

### Community 21 - "Auth Service"
Cohesion: 0.23
Nodes (25): AsyncSession, CurrentUser, Depends, get_db, LoginRequest, PasswordChangeRequest, RefreshTokenRequest, RegisterRequest (+17 more)

### Community 22 - "User Authentication"
Cohesion: 0.10
Nodes (17): User, hash_password(), Hash a password using bcrypt, Verify a password against its hash, verify_password(), Change user password          Args:             user: Current user             c, Get existing user or create new one for OAuth login          Args:             p, Register a new user with email/password          Args:             email: User e (+9 more)

### Community 23 - "GitHub OAuth Service"
Cohesion: 0.10
Nodes (16): datetime, User, AsyncSession, GitHubConnection, GitHubOAuthService, GitHub OAuth service for authentication and token management, Get GitHub user info using access token.          Args:             access_token, Get GitHub user emails.          Args:             access_token: GitHub access t (+8 more)

### Community 24 - "API Responses"
Cohesion: 0.09
Nodes (26): Schema with timestamp fields, TimestampSchema, GitHubConnectionResponse, GitHubRepositoryResponse, GitHub connection response, GitHub repository response, SyncHistoryResponse, get_github_connection_status() (+18 more)

### Community 25 - "Test Configuration"
Cohesion: 0.11
Nodes (25): AsyncClient, AsyncSession, Team, User, admin_auth_headers(), admin_user(), auth_headers(), client() (+17 more)

### Community 26 - "UI Layout"
Cohesion: 0.15
Nodes (16): ThemeToggle(), TopbarProps, Button(), buttonVariants, DropdownMenu(), DropdownMenuCheckboxItem(), DropdownMenuContent(), DropdownMenuItem() (+8 more)

### Community 27 - "User Service"
Cohesion: 0.18
Nodes (22): AsyncSession, CurrentUser, Depends, get_db, UserUpdate, AsyncSession, CurrentAdminUser, Service for user operations (+14 more)

### Community 28 - "Token Encryption"
Cohesion: 0.09
Nodes (15): AsyncSession, generate_encryption_key(), get_token_encryption(), Token encryption utilities using Fernet symmetric encryption, Encrypt and decrypt tokens using Fernet symmetric encryption.     Uses GITHUB_TO, Initialize Fernet with encryption key, Encrypt a string token.          Args:             data: Plain text token to enc, Decrypt an encrypted token.          Args:             encrypted_data: Encrypted (+7 more)

### Community 29 - "Analytics Page"
Cohesion: 0.19
Nodes (17): AnalyticsPage(), DashboardPage(), CommitChart(), DashboardLayout(), DashboardLayoutProps, ProjectCard(), ProjectCardSkeleton(), ProjectGrid() (+9 more)

### Community 30 - "Token Verification"
Cohesion: 0.19
Nodes (20): AsyncSession, Depends, get_db, User, AsyncSession, InvalidTokenError, Verify token and return subject (user_id)      Args:         token: JWT token st, Base security exception (+12 more)

### Community 31 - "Frontend Configuration"
Cohesion: 0.10
Nodes (19): aliases, components, hooks, lib, ui, utils, iconLibrary, registries (+11 more)

### Community 32 - "TypeScript Config"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+11 more)

### Community 33 - "Legacy API"
Cohesion: 0.15
Nodes (18): AsyncSession, get_commit_detail(), get_overview_stats(), get_project(), get_project_commits(), get_timeline_stats(), health_check(), list_projects() (+10 more)

### Community 34 - "Auth Schemas"
Cohesion: 0.15
Nodes (18): LoginRequest, OAuthCallback, PasswordChangeRequest, PasswordResetConfirm, PasswordResetRequest, Authentication schemas, Email/password login request, User registration request (+10 more)

### Community 35 - "Frontend Setup"
Cohesion: 0.12
Nodes (17): Animations Implementation, Dark Mode Implementation, Dashboard Redesign, Next.js Setup, Project Detail Page, Frontend README, Responsive Design, Sidebar Layout (+9 more)

### Community 36 - "User Management"
Cohesion: 0.14
Nodes (7): User, UserUpdate, Deactivate user account          Args:             user: User to deactivate, Activate user account          Args:             user: User to activate, Mark user as verified          Args:             user: User to verify, List users with pagination          Args:             limit: Max results, Update user profile          Args:             user: User to update

### Community 37 - "Team Schemas"
Cohesion: 0.18
Nodes (13): Team member creation schema, Team member update schema, Team member response schema, Team invitation schema, TeamBase, TeamCreate, TeamInvitation, TeamMemberCreate (+5 more)

### Community 38 - "Project Analysis"
Cohesion: 0.25
Nodes (13): analyze_git_repo(), analyze_project(), count_files(), detect_project_type(), main(), Path, Count files by extension, Detect project type/category (+5 more)

### Community 39 - "Frontend Dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, date-fns, framer-motion, lucide-react, next, next-themes (+5 more)

### Community 40 - "Project Discovery"
Cohesion: 0.26
Nodes (11): detect_tech_stack(), find_projects(), get_git_remote(), main(), Path, Convert project name to slug, Find all projects with dev-log, Update config.json with new projects (+3 more)

### Community 41 - "Project Schemas"
Cohesion: 0.21
Nodes (11): CommitSummary, ProjectBase, ProjectCreate, ProjectResponse, ProjectUpdate, ProjectWithStats, Project creation schema, Project update schema (+3 more)

### Community 42 - "Database Migrations"
Cohesion: 0.20
Nodes (10): Connection, do_run_migrations(), Alembic environment configuration, Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations with the given connection, Run migrations in 'online' mode using async engine., Run migrations in 'online' mode.      In this scenario we need to create an Engi, run_async_migrations() (+2 more)

### Community 43 - "Commit Schemas"
Cohesion: 0.25
Nodes (10): CommitBase, CommitCreate, CommitDetail, CommitResponse, CommitSearchResult, CommitUpdate, Commit creation schema, Commit response schema (+2 more)

### Community 44 - "User Schemas"
Cohesion: 0.25
Nodes (10): User in database (includes hashed password), User with team memberships, Team membership info for user response, TeamMembershipInfo, UserBase, UserCreate, UserInDB, UserResponse (+2 more)

### Community 45 - "UI Elements"
Cohesion: 0.33
Nodes (7): ProjectGridProps, Badge(), badgeVariants, Tooltip(), TooltipContent(), TooltipProvider(), TooltipTrigger()

### Community 46 - "Dev Dependencies"
Cohesion: 0.20
Nodes (10): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, tw-animate-css, @types/node, @types/react (+2 more)

### Community 47 - "Project Frontend"
Cohesion: 0.31
Nodes (8): changePage(), handleSearch(), loadCommits(), loadProjectDetails(), projectSlug, renderCommits(), renderPagination(), urlParams

### Community 48 - "Git Log Processing"
Cohesion: 0.33
Nodes (9): generate_devlog_from_git(), get_commit_stats(), main(), parse_commit_type(), Path, Generate dev-logs.json from Git history, Extract commit type from message, Get files changed, lines added/deleted for a commit (+1 more)

### Community 49 - "Package Config"
Cohesion: 0.22
Nodes (8): name, private, scripts, build, dev, lint, start, version

### Community 50 - "Pagination"
Cohesion: 0.22
Nodes (7): PaginatedResponse, PaginationParams, Base schema configurations, Pagination parameters, Paginated response wrapper, CommitListResponse, Paginated commit list response

### Community 51 - "GitHub Client"
Cohesion: 0.25
Nodes (4): datetime, GitHubPagination, GitHub API client service for repository operations, Pagination info from GitHub API

### Community 52 - "App Configuration"
Cohesion: 0.29
Nodes (7): BaseSettings, Config, get_settings(), Application configuration settings, Application settings loaded from environment variables, Get cached settings instance, Settings

### Community 53 - "App Layout"
Cohesion: 0.33
Nodes (4): geistMono, geistSans, metadata, ThemeProvider()

### Community 54 - "JSON Generation"
Cohesion: 0.38
Nodes (6): generate_json_for_project(), main(), parse_devlog_markdown(), Path, Generate dev-logs.json for a single project, Parse a single dev-log markdown file

### Community 55 - "App Constants"
Cohesion: 0.33
Nodes (5): API_CONFIG, BREAKPOINTS, CHART_COLORS, COMMIT_TYPE_LABELS, NAV_ITEMS

### Community 56 - "Dashboard Scripts"
Cohesion: 0.53
Nodes (4): loadDashboard(), renderProjects(), renderRecentActivity(), renderTypeChart()

### Community 57 - "Base Model"
Cohesion: 0.50
Nodes (4): datetime, Base model with common fields, Return current UTC time, utcnow()

### Community 58 - "Sync Script"
Cohesion: 0.60
Nodes (4): load_config(), main(), Sync single project to database, sync_project()

### Community 59 - "Start Scripts"
Cohesion: 0.70
Nodes (4): start_backend(), start_frontend(), start_legacy(), start.sh script

### Community 60 - "Token Management"
Cohesion: 0.50
Nodes (3): Create access and refresh tokens for user          Args:             user: Authe, Refresh access token using refresh token          Args:             refresh_toke, Token

### Community 62 - "HTML Generation"
Cohesion: 0.67
Nodes (3): generate_html(), main(), Generate HTML for a project

### Community 63 - "Script Installation"
Cohesion: 0.67
Nodes (3): install_scripts(), main(), Install HTML generation scripts to a project

### Community 65 - "Legacy Pages"
Cohesion: 0.67
Nodes (3): Legacy Index Page, Legacy Project Page, Legacy Search Page

## Knowledge Gaps
- **170 isolated node(s):** `Config`, `AsyncSession`, `GitHubBranchInfo`, `GitHubPullRequestInfo`, `GitHubIssueInfo` (+165 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Team Management` to `Webhook Handling`, `Database Models`, `User Management`, `GitHub API Errors`, `Token Management`, `Team Endpoints`, `Team Service`, `Auth Service`, `User Authentication`, `GitHub OAuth Service`, `Test Configuration`, `User Service`, `Token Encryption`, `Access Control`, `Token Verification`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `TimestampSchema` connect `API Responses` to `Webhook Handling`, `Auth Schemas`, `Team Schemas`, `Project Schemas`, `Commit Schemas`, `User Schemas`, `Pagination`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `BaseSchema` connect `Auth Schemas` to `Team Schemas`, `Project Schemas`, `Commit Schemas`, `GitHub Schemas`, `User Schemas`, `Pagination`, `API Responses`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 76 inferred relationships involving `User` (e.g. with `AsyncSession` and `User`) actually correct?**
  _`User` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `Project` (e.g. with `AsyncSession` and `AsyncSession`) actually correct?**
  _`Project` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `TeamMember` (e.g. with `AsyncSession` and `CurrentUser`) actually correct?**
  _`TeamMember` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `TeamService` (e.g. with `AsyncSession` and `CurrentUser`) actually correct?**
  _`TeamService` has 29 INFERRED edges - model-reasoned connections that need verification._