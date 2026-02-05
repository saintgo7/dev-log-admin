"""
Repository synchronization service
"""
import json
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.project import Project
from app.models.commit import Commit
from app.models.github import (
    GitHubRepository,
    GitHubConnection,
    SyncHistory,
    SyncStatus,
)
from app.services.github_client_service import GitHubClient, GitHubAPIError
from app.services.github_oauth_service import GitHubOAuthService


class SyncError(Exception):
    """Sync operation error"""
    pass


class SyncService:
    """
    Service for synchronizing GitHub repositories with local data.
    Handles commits, issues, and pull requests sync.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.oauth_service = GitHubOAuthService(db)

    async def get_github_client(self, user_id: str) -> GitHubClient:
        """
        Get GitHub client for a user.

        Args:
            user_id: User ID

        Returns:
            GitHubClient instance

        Raises:
            SyncError: If no valid GitHub connection exists
        """
        access_token = await self.oauth_service.get_decrypted_token(user_id)
        if not access_token:
            raise SyncError("No valid GitHub connection found")
        return GitHubClient(access_token)

    async def link_repository(
        self,
        user_id: str,
        project_id: str,
        owner: str,
        name: str,
    ) -> GitHubRepository:
        """
        Link a GitHub repository to a project.

        Args:
            user_id: User ID (for GitHub API access)
            project_id: Project to link
            owner: Repository owner
            name: Repository name

        Returns:
            Created GitHubRepository
        """
        # Check if project exists
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise SyncError(f"Project not found: {project_id}")

        # Check if already linked
        result = await self.db.execute(
            select(GitHubRepository).where(GitHubRepository.project_id == project_id)
        )
        if result.scalar_one_or_none():
            raise SyncError("Project already linked to a GitHub repository")

        # Get repository info from GitHub
        async with await self.get_github_client(user_id) as client:
            try:
                repo_data = await client.get_repo(owner, name)
            except GitHubAPIError as e:
                raise SyncError(f"Failed to get repository info: {e}")

        # Create GitHubRepository
        github_repo = GitHubRepository(
            id=str(uuid4()),
            project_id=project_id,
            github_repo_id=str(repo_data["id"]),
            owner=repo_data["owner"]["login"],
            name=repo_data["name"],
            full_name=repo_data["full_name"],
            description=repo_data.get("description"),
            html_url=repo_data["html_url"],
            clone_url=repo_data.get("clone_url"),
            ssh_url=repo_data.get("ssh_url"),
            default_branch=repo_data.get("default_branch", "main"),
            is_private=repo_data.get("private", False),
            is_fork=repo_data.get("fork", False),
            language=repo_data.get("language"),
            topics=json.dumps(repo_data.get("topics", [])),
            stars_count=repo_data.get("stargazers_count", 0),
            forks_count=repo_data.get("forks_count", 0),
            watchers_count=repo_data.get("watchers_count", 0),
            open_issues_count=repo_data.get("open_issues_count", 0),
        )

        self.db.add(github_repo)

        # Update project with repository URL
        project.repository_url = repo_data["html_url"]
        project.html_url = repo_data["html_url"]

        await self.db.flush()
        await self.db.refresh(github_repo)

        return github_repo

    async def unlink_repository(self, project_id: str) -> bool:
        """
        Unlink a GitHub repository from a project.

        Args:
            project_id: Project ID

        Returns:
            True if unlinked, False if not found
        """
        result = await self.db.execute(
            select(GitHubRepository).where(GitHubRepository.project_id == project_id)
        )
        github_repo = result.scalar_one_or_none()
        if not github_repo:
            return False

        await self.db.delete(github_repo)
        await self.db.flush()
        return True

    async def list_available_repositories(
        self,
        user_id: str,
        per_page: int = 50,
        max_items: int = 200,
    ) -> List[dict]:
        """
        List available GitHub repositories for linking.

        Args:
            user_id: User ID
            per_page: Items per page
            max_items: Maximum items to return

        Returns:
            List of repository data
        """
        async with await self.get_github_client(user_id) as client:
            repos = await client.list_user_repos(
                per_page=per_page,
                max_items=max_items,
                type="all",
            )
            return repos

    async def sync_repository(
        self,
        user_id: str,
        repository_id: str,
        sync_commits: bool = True,
        sync_issues: bool = False,
        sync_prs: bool = False,
        full_sync: bool = False,
    ) -> SyncHistory:
        """
        Synchronize a GitHub repository.

        Args:
            user_id: User ID (for GitHub API access)
            repository_id: GitHubRepository ID
            sync_commits: Sync commits
            sync_issues: Sync issues
            sync_prs: Sync pull requests
            full_sync: Full sync or incremental

        Returns:
            SyncHistory record
        """
        # Get repository
        result = await self.db.execute(
            select(GitHubRepository).where(GitHubRepository.id == repository_id)
        )
        github_repo = result.scalar_one_or_none()
        if not github_repo:
            raise SyncError(f"Repository not found: {repository_id}")

        # Create sync history record
        sync_history = SyncHistory(
            id=str(uuid4()),
            repository_id=repository_id,
            sync_type="manual",
            status=SyncStatus.IN_PROGRESS.value,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(sync_history)
        await self.db.flush()

        try:
            async with await self.get_github_client(user_id) as client:
                commits_synced = 0
                issues_synced = 0
                prs_synced = 0

                # Update repository metadata
                repo_data = await client.get_repo(github_repo.owner, github_repo.name)
                await self._update_repo_metadata(github_repo, repo_data)

                # Sync commits
                if sync_commits:
                    commits_synced = await self._sync_commits(
                        client,
                        github_repo,
                        full_sync=full_sync,
                    )

                # Sync issues
                if sync_issues:
                    issues_synced = await self._sync_issues(
                        client,
                        github_repo,
                        full_sync=full_sync,
                    )

                # Sync pull requests
                if sync_prs:
                    prs_synced = await self._sync_pull_requests(
                        client,
                        github_repo,
                        full_sync=full_sync,
                    )

            # Update sync history
            sync_history.status = SyncStatus.COMPLETED.value
            sync_history.completed_at = datetime.now(timezone.utc)
            sync_history.commits_synced = commits_synced
            sync_history.issues_synced = issues_synced
            sync_history.prs_synced = prs_synced

            # Update repository sync state
            github_repo.last_sync_at = datetime.now(timezone.utc)
            github_repo.last_sync_status = SyncStatus.COMPLETED.value
            github_repo.last_sync_error = None

            await self.db.flush()
            await self.db.refresh(sync_history)

        except Exception as e:
            # Update sync history with error
            sync_history.status = SyncStatus.FAILED.value
            sync_history.completed_at = datetime.now(timezone.utc)
            sync_history.error_message = str(e)

            # Update repository sync state
            github_repo.last_sync_status = SyncStatus.FAILED.value
            github_repo.last_sync_error = str(e)

            await self.db.flush()
            await self.db.refresh(sync_history)
            raise SyncError(f"Sync failed: {e}")

        return sync_history

    async def _update_repo_metadata(
        self,
        github_repo: GitHubRepository,
        repo_data: dict,
    ) -> None:
        """Update repository metadata from GitHub API response"""
        github_repo.description = repo_data.get("description")
        github_repo.default_branch = repo_data.get("default_branch", "main")
        github_repo.is_private = repo_data.get("private", False)
        github_repo.is_fork = repo_data.get("fork", False)
        github_repo.language = repo_data.get("language")
        github_repo.topics = json.dumps(repo_data.get("topics", []))
        github_repo.stars_count = repo_data.get("stargazers_count", 0)
        github_repo.forks_count = repo_data.get("forks_count", 0)
        github_repo.watchers_count = repo_data.get("watchers_count", 0)
        github_repo.open_issues_count = repo_data.get("open_issues_count", 0)

    async def _sync_commits(
        self,
        client: GitHubClient,
        github_repo: GitHubRepository,
        full_sync: bool = False,
    ) -> int:
        """
        Sync commits from GitHub to local database.

        Returns:
            Number of commits synced
        """
        # Determine starting point
        since = None
        if not full_sync and github_repo.last_sync_at:
            since = github_repo.last_sync_at

        # Fetch commits from GitHub
        commits = await client.list_commits(
            owner=github_repo.owner,
            repo=github_repo.name,
            since=since,
            per_page=settings.SYNC_BATCH_SIZE,
            max_items=settings.SYNC_MAX_COMMITS_PER_REPO,
        )

        if not commits:
            return 0

        # Get existing commit SHAs
        result = await self.db.execute(
            select(Commit.sha).where(Commit.project_id == github_repo.project_id)
        )
        existing_shas = {row[0] for row in result.fetchall()}

        # Insert new commits
        new_commits = []
        for commit_info in commits:
            if commit_info.sha in existing_shas:
                continue

            # Parse commit message for type and scope
            message = commit_info.message
            commit_type = "chore"  # default
            subject = message.split("\n")[0] if message else ""

            # Try to parse conventional commit format
            if ":" in subject:
                prefix = subject.split(":")[0].lower()
                if prefix.startswith("feat"):
                    commit_type = "feat"
                elif prefix.startswith("fix"):
                    commit_type = "fix"
                elif prefix.startswith("docs"):
                    commit_type = "docs"
                elif prefix.startswith("refactor"):
                    commit_type = "refactor"
                elif prefix.startswith("test"):
                    commit_type = "test"
                elif prefix.startswith("perf"):
                    commit_type = "perf"
                elif prefix.startswith("style"):
                    commit_type = "style"

            new_commit = Commit(
                id=str(uuid4()),
                project_id=github_repo.project_id,
                sha=commit_info.sha,
                message=message,
                author=commit_info.author_name,
                author_email=commit_info.author_email,
                commit_date=commit_info.author_date,
                commit_type=commit_type,
                files_changed=commit_info.files_changed,
                insertions=commit_info.additions,
                deletions=commit_info.deletions,
                url=commit_info.url,
            )
            new_commits.append(new_commit)

        if new_commits:
            self.db.add_all(new_commits)

            # Update last commit SHA
            github_repo.last_commit_sha = commits[0].sha

            # Update project total commits
            result = await self.db.execute(
                select(Project).where(Project.id == github_repo.project_id)
            )
            project = result.scalar_one_or_none()
            if project:
                project.total_commits = (project.total_commits or 0) + len(new_commits)
                project.last_synced_at = datetime.now(timezone.utc)

            await self.db.flush()

        return len(new_commits)

    async def _sync_issues(
        self,
        client: GitHubClient,
        github_repo: GitHubRepository,
        full_sync: bool = False,
    ) -> int:
        """
        Sync issues from GitHub.
        Note: This is a placeholder - implement based on your Issue model.

        Returns:
            Number of issues synced
        """
        # TODO: Implement issue sync when Issue model is available
        # issues = await client.list_issues(
        #     owner=github_repo.owner,
        #     repo=github_repo.name,
        # )
        return 0

    async def _sync_pull_requests(
        self,
        client: GitHubClient,
        github_repo: GitHubRepository,
        full_sync: bool = False,
    ) -> int:
        """
        Sync pull requests from GitHub.
        Note: This is a placeholder - implement based on your PR model.

        Returns:
            Number of PRs synced
        """
        # TODO: Implement PR sync when PullRequest model is available
        # prs = await client.list_pull_requests(
        #     owner=github_repo.owner,
        #     repo=github_repo.name,
        # )
        return 0

    async def get_sync_status(
        self,
        repository_id: str,
    ) -> Tuple[Optional[SyncHistory], int]:
        """
        Get sync status for a repository.

        Args:
            repository_id: GitHubRepository ID

        Returns:
            Tuple of (last_sync_history, pending_syncs_count)
        """
        # Get last sync
        result = await self.db.execute(
            select(SyncHistory)
            .where(SyncHistory.repository_id == repository_id)
            .order_by(SyncHistory.created_at.desc())
            .limit(1)
        )
        last_sync = result.scalar_one_or_none()

        # Count pending syncs
        result = await self.db.execute(
            select(SyncHistory)
            .where(
                SyncHistory.repository_id == repository_id,
                SyncHistory.status.in_([
                    SyncStatus.PENDING.value,
                    SyncStatus.IN_PROGRESS.value,
                ]),
            )
        )
        pending_count = len(result.scalars().all())

        return last_sync, pending_count

    async def get_sync_history(
        self,
        repository_id: str,
        limit: int = 10,
    ) -> List[SyncHistory]:
        """
        Get sync history for a repository.

        Args:
            repository_id: GitHubRepository ID
            limit: Maximum records to return

        Returns:
            List of SyncHistory records
        """
        result = await self.db.execute(
            select(SyncHistory)
            .where(SyncHistory.repository_id == repository_id)
            .order_by(SyncHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
