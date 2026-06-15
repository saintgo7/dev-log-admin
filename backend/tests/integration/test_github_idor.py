# GitHub 저장소/동기화 엔드포인트의 IDOR(소유권 미검증) 회귀 테스트
"""
Regression tests for IDOR on GitHub repository / sync / webhook endpoints.

A logged-in user who is NOT a member of the team that owns a project must not
be able to read, modify, delete, or sync that project's linked GitHub
repository, nor read its webhook events.
"""
import pytest
import pytest_asyncio
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.team import Team, TeamMember
from app.models.project import Project
from app.models.github import GitHubRepository, WebhookEvent
from app.core.security import hash_password, create_access_token


@pytest.fixture
def attacker_headers(attacker_user: User) -> dict:
    token = create_access_token(subject=attacker_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(admin_user: User) -> dict:
    token = create_access_token(subject=admin_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def attacker_user(db_session: AsyncSession) -> User:
    """A second authenticated user who owns nothing."""
    user = User(
        id=str(uuid4()),
        email="attacker@example.com",
        name="Attacker",
        hashed_password=hash_password("password123"),
        is_active=True,
        is_verified=True,
        role="member",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def owned_repository(
    db_session: AsyncSession,
    test_team: Team,
) -> GitHubRepository:
    """A GitHub repository linked to a private project owned by test_team."""
    project = Project(
        id=str(uuid4()),
        slug="owned-project",
        name="Owned Project",
        team_id=test_team.id,
        visibility="private",
    )
    db_session.add(project)
    await db_session.flush()

    repo = GitHubRepository(
        id=str(uuid4()),
        project_id=project.id,
        github_repo_id="123456",
        owner="owner-org",
        name="secret-repo",
        full_name="owner-org/secret-repo",
        html_url="https://github.com/owner-org/secret-repo",
    )
    db_session.add(repo)
    await db_session.commit()
    await db_session.refresh(repo)
    return repo


class TestRepositoryIDOR:
    """An outsider must get 403 on another team's repository endpoints."""

    @pytest.mark.asyncio
    async def test_get_repository_forbidden(
        self, client: AsyncClient, attacker_headers: dict, owned_repository
    ):
        r = await client.get(
            f"/api/v2/github/repositories/{owned_repository.id}",
            headers=attacker_headers,
        )
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_patch_repository_forbidden(
        self, client: AsyncClient, attacker_headers: dict, owned_repository
    ):
        r = await client.patch(
            f"/api/v2/github/repositories/{owned_repository.id}",
            headers=attacker_headers,
            json={"sync_enabled": False},
        )
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_repository_forbidden(
        self, client: AsyncClient, attacker_headers: dict, owned_repository
    ):
        r = await client.delete(
            f"/api/v2/github/repositories/{owned_repository.id}",
            headers=attacker_headers,
        )
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_sync_repository_forbidden(
        self, client: AsyncClient, attacker_headers: dict, owned_repository
    ):
        r = await client.post(
            f"/api/v2/github/repositories/{owned_repository.id}/sync",
            headers=attacker_headers,
        )
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_sync_status_forbidden(
        self, client: AsyncClient, attacker_headers: dict, owned_repository
    ):
        r = await client.get(
            f"/api/v2/github/repositories/{owned_repository.id}/sync/status",
            headers=attacker_headers,
        )
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_sync_history_forbidden(
        self, client: AsyncClient, attacker_headers: dict, owned_repository
    ):
        r = await client.get(
            f"/api/v2/github/repositories/{owned_repository.id}/sync/history",
            headers=attacker_headers,
        )
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_owner_can_read_repository(
        self, client: AsyncClient, auth_headers: dict, owned_repository
    ):
        """The team owner (test_user) still has access (no regression)."""
        r = await client.get(
            f"/api/v2/github/repositories/{owned_repository.id}",
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert r.json()["id"] == owned_repository.id


class TestLinkRepositoryIDOR:
    """Linking a repo to a project the user does not own must be rejected."""

    @pytest.mark.asyncio
    async def test_link_to_foreign_project_forbidden(
        self, client: AsyncClient, attacker_headers: dict, owned_repository
    ):
        r = await client.post(
            "/api/v2/github/repositories",
            headers=attacker_headers,
            json={
                "project_id": owned_repository.project_id,
                "owner": "x",
                "name": "y",
            },
        )
        # 403 before any GitHub call (was 400 "no connection" pre-fix)
        assert r.status_code == 403


class TestWebhookEventIDOR:
    """Webhook event reads must be scoped to repository ownership."""

    @pytest_asyncio.fixture
    async def owned_event(
        self, db_session: AsyncSession, owned_repository
    ) -> WebhookEvent:
        event = WebhookEvent(
            id=str(uuid4()),
            repository_id=owned_repository.id,
            event_type="push",
            delivery_id=str(uuid4()),
            payload={"secret": "private repo payload"},
            processed=True,
        )
        db_session.add(event)
        await db_session.commit()
        await db_session.refresh(event)
        return event

    @pytest.mark.asyncio
    async def test_get_event_forbidden(
        self, client: AsyncClient, attacker_headers: dict, owned_event
    ):
        r = await client.get(
            f"/api/v2/webhooks/github/events/{owned_event.id}",
            headers=attacker_headers,
        )
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_list_events_for_foreign_repo_forbidden(
        self, client: AsyncClient, attacker_headers: dict, owned_repository
    ):
        r = await client.get(
            "/api/v2/webhooks/github/events",
            headers=attacker_headers,
            params={"repository_id": owned_repository.id},
        )
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_list_all_events_requires_admin(
        self, client: AsyncClient, attacker_headers: dict
    ):
        """Cross-repository listing (no repository_id) is admin-only."""
        r = await client.get(
            "/api/v2/webhooks/github/events",
            headers=attacker_headers,
        )
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_can_list_all_events(
        self, client: AsyncClient, admin_headers: dict
    ):
        r = await client.get(
            "/api/v2/webhooks/github/events",
            headers=admin_headers,
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    @pytest.mark.asyncio
    async def test_owner_can_read_event(
        self, client: AsyncClient, auth_headers: dict, owned_event
    ):
        r = await client.get(
            f"/api/v2/webhooks/github/events/{owned_event.id}",
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert r.json()["id"] == owned_event.id
