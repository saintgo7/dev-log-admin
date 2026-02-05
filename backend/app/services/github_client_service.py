"""
GitHub API client service for repository operations
"""
import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Any
from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.schemas.github import (
    GitHubUserInfo,
    GitHubCommitInfo,
    GitHubBranchInfo,
    GitHubPullRequestInfo,
    GitHubIssueInfo,
    GitHubRateLimitInfo,
)


class GitHubAPIError(Exception):
    """GitHub API error"""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class GitHubRateLimitError(GitHubAPIError):
    """GitHub API rate limit exceeded"""

    def __init__(self, reset_at: datetime):
        super().__init__(
            f"GitHub API rate limit exceeded. Resets at {reset_at}",
            status_code=403
        )
        self.reset_at = reset_at


@dataclass
class GitHubPagination:
    """Pagination info from GitHub API"""
    page: int
    per_page: int
    has_next: bool
    total_count: Optional[int] = None


class GitHubClient:
    """
    Async GitHub API client.
    Handles API requests with rate limiting and pagination.
    """

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = settings.GITHUB_API_BASE_URL
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "GitHubClient":
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> tuple[Any, dict]:
        """
        Make an API request with error handling.

        Returns:
            Tuple of (response_json, headers)
        """
        response = await self._client.request(method, path, **kwargs)

        # Check rate limit
        remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
        if remaining == 0:
            reset_timestamp = int(response.headers.get("X-RateLimit-Reset", 0))
            reset_at = datetime.fromtimestamp(reset_timestamp, tz=timezone.utc)
            raise GitHubRateLimitError(reset_at)

        if response.status_code == 404:
            raise GitHubAPIError("Resource not found", status_code=404)

        if response.status_code == 401:
            raise GitHubAPIError("Unauthorized - token may be invalid", status_code=401)

        if response.status_code == 403:
            raise GitHubAPIError(
                "Forbidden - insufficient permissions",
                status_code=403,
                response=response.json() if response.content else None
            )

        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise GitHubAPIError(
                error_data.get("message", f"API error: {response.status_code}"),
                status_code=response.status_code,
                response=error_data
            )

        return response.json() if response.content else None, dict(response.headers)

    async def _paginate(
        self,
        path: str,
        per_page: int = 100,
        max_items: int = None,
        **kwargs
    ) -> List[Any]:
        """
        Paginate through all results.

        Args:
            path: API endpoint path
            per_page: Items per page
            max_items: Maximum items to fetch
            **kwargs: Additional request params

        Returns:
            List of all items
        """
        items = []
        page = 1

        while True:
            params = kwargs.get("params", {})
            params.update({"page": page, "per_page": per_page})
            kwargs["params"] = params

            data, headers = await self._request("GET", path, **kwargs)

            if not data:
                break

            items.extend(data)

            if max_items and len(items) >= max_items:
                items = items[:max_items]
                break

            # Check for next page
            link_header = headers.get("Link", "")
            if 'rel="next"' not in link_header:
                break

            page += 1

        return items

    # ========================================================================
    # User Operations
    # ========================================================================

    async def get_current_user(self) -> GitHubUserInfo:
        """Get current authenticated user info"""
        data, _ = await self._request("GET", "/user")
        return GitHubUserInfo(**data)

    async def get_user(self, username: str) -> GitHubUserInfo:
        """Get user info by username"""
        data, _ = await self._request("GET", f"/users/{username}")
        return GitHubUserInfo(**data)

    # ========================================================================
    # Repository Operations
    # ========================================================================

    async def list_user_repos(
        self,
        per_page: int = 100,
        max_items: int = None,
        sort: str = "updated",
        direction: str = "desc",
        type: str = "all",
    ) -> List[dict]:
        """
        List repositories for authenticated user.

        Args:
            per_page: Items per page
            max_items: Maximum repos to fetch
            sort: Sort by (created, updated, pushed, full_name)
            direction: Sort direction (asc, desc)
            type: Type of repos (all, owner, public, private, member)
        """
        return await self._paginate(
            "/user/repos",
            per_page=per_page,
            max_items=max_items,
            params={"sort": sort, "direction": direction, "type": type},
        )

    async def get_repo(self, owner: str, repo: str) -> dict:
        """Get repository info"""
        data, _ = await self._request("GET", f"/repos/{owner}/{repo}")
        return data

    async def list_branches(
        self,
        owner: str,
        repo: str,
        per_page: int = 100,
    ) -> List[GitHubBranchInfo]:
        """List repository branches"""
        data = await self._paginate(
            f"/repos/{owner}/{repo}/branches",
            per_page=per_page,
        )
        return [
            GitHubBranchInfo(
                name=b["name"],
                sha=b["commit"]["sha"],
                protected=b.get("protected", False),
            )
            for b in data
        ]

    # ========================================================================
    # Commit Operations
    # ========================================================================

    async def list_commits(
        self,
        owner: str,
        repo: str,
        sha: str = None,
        since: datetime = None,
        until: datetime = None,
        per_page: int = 100,
        max_items: int = None,
    ) -> List[GitHubCommitInfo]:
        """
        List repository commits.

        Args:
            owner: Repository owner
            repo: Repository name
            sha: SHA or branch to start from
            since: Only commits after this date
            until: Only commits before this date
            per_page: Items per page
            max_items: Maximum commits to fetch
        """
        params = {}
        if sha:
            params["sha"] = sha
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()

        data = await self._paginate(
            f"/repos/{owner}/{repo}/commits",
            per_page=per_page,
            max_items=max_items,
            params=params,
        )

        commits = []
        for c in data:
            commit_data = c.get("commit", {})
            author = commit_data.get("author", {})
            committer = commit_data.get("committer", {})

            commits.append(GitHubCommitInfo(
                sha=c["sha"],
                message=commit_data.get("message", ""),
                author_name=author.get("name", "Unknown"),
                author_email=author.get("email", ""),
                author_date=datetime.fromisoformat(
                    author.get("date", "").replace("Z", "+00:00")
                ) if author.get("date") else datetime.now(timezone.utc),
                committer_name=committer.get("name"),
                committer_email=committer.get("email"),
                committer_date=datetime.fromisoformat(
                    committer.get("date", "").replace("Z", "+00:00")
                ) if committer.get("date") else None,
                url=c.get("html_url", ""),
                additions=c.get("stats", {}).get("additions", 0),
                deletions=c.get("stats", {}).get("deletions", 0),
                files_changed=len(c.get("files", [])),
            ))

        return commits

    async def get_commit(self, owner: str, repo: str, sha: str) -> GitHubCommitInfo:
        """Get a specific commit with full details"""
        data, _ = await self._request("GET", f"/repos/{owner}/{repo}/commits/{sha}")

        commit_data = data.get("commit", {})
        author = commit_data.get("author", {})
        committer = commit_data.get("committer", {})
        stats = data.get("stats", {})

        return GitHubCommitInfo(
            sha=data["sha"],
            message=commit_data.get("message", ""),
            author_name=author.get("name", "Unknown"),
            author_email=author.get("email", ""),
            author_date=datetime.fromisoformat(
                author.get("date", "").replace("Z", "+00:00")
            ),
            committer_name=committer.get("name"),
            committer_email=committer.get("email"),
            committer_date=datetime.fromisoformat(
                committer.get("date", "").replace("Z", "+00:00")
            ) if committer.get("date") else None,
            url=data.get("html_url", ""),
            additions=stats.get("additions", 0),
            deletions=stats.get("deletions", 0),
            files_changed=len(data.get("files", [])),
        )

    # ========================================================================
    # Pull Request Operations
    # ========================================================================

    async def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        sort: str = "updated",
        direction: str = "desc",
        per_page: int = 100,
        max_items: int = None,
    ) -> List[GitHubPullRequestInfo]:
        """
        List repository pull requests.

        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state (open, closed, all)
            sort: Sort by (created, updated, popularity, long-running)
            direction: Sort direction
            per_page: Items per page
            max_items: Maximum PRs to fetch
        """
        data = await self._paginate(
            f"/repos/{owner}/{repo}/pulls",
            per_page=per_page,
            max_items=max_items,
            params={"state": state, "sort": sort, "direction": direction},
        )

        prs = []
        for pr in data:
            prs.append(GitHubPullRequestInfo(
                number=pr["number"],
                title=pr["title"],
                state=pr["state"],
                body=pr.get("body"),
                user_login=pr["user"]["login"],
                head_ref=pr["head"]["ref"],
                base_ref=pr["base"]["ref"],
                created_at=datetime.fromisoformat(
                    pr["created_at"].replace("Z", "+00:00")
                ),
                updated_at=datetime.fromisoformat(
                    pr["updated_at"].replace("Z", "+00:00")
                ),
                merged_at=datetime.fromisoformat(
                    pr["merged_at"].replace("Z", "+00:00")
                ) if pr.get("merged_at") else None,
                closed_at=datetime.fromisoformat(
                    pr["closed_at"].replace("Z", "+00:00")
                ) if pr.get("closed_at") else None,
                html_url=pr["html_url"],
            ))

        return prs

    # ========================================================================
    # Issue Operations
    # ========================================================================

    async def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        sort: str = "updated",
        direction: str = "desc",
        per_page: int = 100,
        max_items: int = None,
    ) -> List[GitHubIssueInfo]:
        """
        List repository issues (excludes PRs).

        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            sort: Sort by (created, updated, comments)
            direction: Sort direction
            per_page: Items per page
            max_items: Maximum issues to fetch
        """
        data = await self._paginate(
            f"/repos/{owner}/{repo}/issues",
            per_page=per_page,
            max_items=max_items,
            params={"state": state, "sort": sort, "direction": direction},
        )

        issues = []
        for issue in data:
            # Skip pull requests (they appear in issues API too)
            if "pull_request" in issue:
                continue

            issues.append(GitHubIssueInfo(
                number=issue["number"],
                title=issue["title"],
                state=issue["state"],
                body=issue.get("body"),
                user_login=issue["user"]["login"],
                labels=[l["name"] for l in issue.get("labels", [])],
                assignees=[a["login"] for a in issue.get("assignees", [])],
                created_at=datetime.fromisoformat(
                    issue["created_at"].replace("Z", "+00:00")
                ),
                updated_at=datetime.fromisoformat(
                    issue["updated_at"].replace("Z", "+00:00")
                ),
                closed_at=datetime.fromisoformat(
                    issue["closed_at"].replace("Z", "+00:00")
                ) if issue.get("closed_at") else None,
                html_url=issue["html_url"],
            ))

        return issues

    # ========================================================================
    # Webhook Operations
    # ========================================================================

    async def list_webhooks(self, owner: str, repo: str) -> List[dict]:
        """List repository webhooks"""
        data, _ = await self._request("GET", f"/repos/{owner}/{repo}/hooks")
        return data

    async def create_webhook(
        self,
        owner: str,
        repo: str,
        webhook_url: str,
        secret: str,
        events: List[str] = None,
    ) -> dict:
        """
        Create a webhook for a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            webhook_url: URL to receive webhook events
            secret: Webhook secret for signature verification
            events: List of events to subscribe to
        """
        events = events or ["push", "pull_request", "issues"]

        data, _ = await self._request(
            "POST",
            f"/repos/{owner}/{repo}/hooks",
            json={
                "name": "web",
                "active": True,
                "events": events,
                "config": {
                    "url": webhook_url,
                    "content_type": "json",
                    "secret": secret,
                    "insecure_ssl": "0",
                },
            },
        )
        return data

    async def delete_webhook(self, owner: str, repo: str, hook_id: str) -> None:
        """Delete a webhook"""
        await self._request("DELETE", f"/repos/{owner}/{repo}/hooks/{hook_id}")

    async def ping_webhook(self, owner: str, repo: str, hook_id: str) -> None:
        """Ping a webhook to test it"""
        await self._request("POST", f"/repos/{owner}/{repo}/hooks/{hook_id}/pings")

    # ========================================================================
    # Rate Limit
    # ========================================================================

    async def get_rate_limit(self) -> GitHubRateLimitInfo:
        """Get current rate limit status"""
        data, _ = await self._request("GET", "/rate_limit")
        core = data["resources"]["core"]
        return GitHubRateLimitInfo(
            limit=core["limit"],
            remaining=core["remaining"],
            reset_at=datetime.fromtimestamp(core["reset"], tz=timezone.utc),
            used=core["used"],
        )
