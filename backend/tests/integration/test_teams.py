"""
Integration tests for team endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCreateTeam:
    """Tests for POST /api/v2/teams endpoint"""

    async def test_create_team_success(self, client: AsyncClient, auth_headers):
        """Should create team successfully"""
        response = await client.post(
            "/api/v2/teams",
            headers=auth_headers,
            json={
                "name": "My Team",
                "slug": "my-team",
                "description": "A test team"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Team"
        assert data["slug"] == "my-team"
        assert data["plan"] == "free"
        assert "id" in data

    async def test_create_team_duplicate_slug(
        self, client: AsyncClient, test_team, auth_headers
    ):
        """Should reject duplicate slug"""
        response = await client.post(
            "/api/v2/teams",
            headers=auth_headers,
            json={
                "name": "Another Team",
                "slug": test_team.slug
            }
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    async def test_create_team_invalid_slug(self, client: AsyncClient, auth_headers):
        """Should reject invalid slug format"""
        response = await client.post(
            "/api/v2/teams",
            headers=auth_headers,
            json={
                "name": "My Team",
                "slug": "Invalid Slug!"  # Contains invalid characters
            }
        )

        assert response.status_code == 422

    async def test_create_team_unauthenticated(self, client: AsyncClient):
        """Should reject unauthenticated request"""
        response = await client.post(
            "/api/v2/teams",
            json={
                "name": "My Team",
                "slug": "my-team"
            }
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestListTeams:
    """Tests for GET /api/v2/teams endpoint"""

    async def test_list_teams_success(
        self, client: AsyncClient, test_team, auth_headers
    ):
        """Should list user's teams"""
        response = await client.get("/api/v2/teams", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(t["id"] == test_team.id for t in data)

    async def test_list_teams_empty(self, client: AsyncClient, admin_auth_headers):
        """Should return empty list for user with no teams"""
        response = await client.get("/api/v2/teams", headers=admin_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
class TestGetTeam:
    """Tests for GET /api/v2/teams/{team_id} endpoint"""

    async def test_get_team_success(
        self, client: AsyncClient, test_team, auth_headers
    ):
        """Should return team details"""
        response = await client.get(
            f"/api/v2/teams/{test_team.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_team.id
        assert data["name"] == test_team.name
        assert "members" in data
        assert "member_count" in data

    async def test_get_team_not_member(
        self, client: AsyncClient, test_team, admin_auth_headers
    ):
        """Should reject non-member access"""
        response = await client.get(
            f"/api/v2/teams/{test_team.id}",
            headers=admin_auth_headers
        )

        assert response.status_code == 403

    async def test_get_team_not_found(self, client: AsyncClient, auth_headers):
        """Should return 404 for nonexistent team"""
        response = await client.get(
            "/api/v2/teams/nonexistent-id",
            headers=auth_headers
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestUpdateTeam:
    """Tests for PATCH /api/v2/teams/{team_id} endpoint"""

    async def test_update_team_success(
        self, client: AsyncClient, test_team, auth_headers
    ):
        """Should update team successfully"""
        response = await client.patch(
            f"/api/v2/teams/{test_team.id}",
            headers=auth_headers,
            json={"name": "Updated Team Name"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Team Name"

    async def test_update_team_not_admin(
        self, client: AsyncClient, test_team, admin_auth_headers
    ):
        """Should reject non-admin update"""
        response = await client.patch(
            f"/api/v2/teams/{test_team.id}",
            headers=admin_auth_headers,
            json={"name": "New Name"}
        )

        assert response.status_code == 403


@pytest.mark.asyncio
class TestTeamMembers:
    """Tests for team member endpoints"""

    async def test_list_members(
        self, client: AsyncClient, test_team, auth_headers
    ):
        """Should list team members"""
        response = await client.get(
            f"/api/v2/teams/{test_team.id}/members",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_add_member_user_not_found(
        self, client: AsyncClient, test_team, auth_headers
    ):
        """Should reject adding nonexistent user"""
        response = await client.post(
            f"/api/v2/teams/{test_team.id}/members",
            headers=auth_headers,
            json={
                "email": "nonexistent@example.com",
                "role": "member"
            }
        )

        assert response.status_code == 404

    async def test_remove_self(
        self, client: AsyncClient, test_team, test_user, auth_headers
    ):
        """Owner should not be able to remove themselves"""
        response = await client.delete(
            f"/api/v2/teams/{test_team.id}/members/{test_user.id}",
            headers=auth_headers
        )

        # Owner cannot be removed
        assert response.status_code == 400
