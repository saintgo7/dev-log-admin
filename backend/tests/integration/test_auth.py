"""
Integration tests for authentication endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    """Tests for /api/v2/auth/register endpoint"""

    async def test_register_success(self, client: AsyncClient):
        """Should register new user successfully"""
        response = await client.post(
            "/api/v2/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "name": "New User"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Should reject duplicate email"""
        response = await client.post(
            "/api/v2/auth/register",
            json={
                "email": test_user.email,
                "password": "password123"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    async def test_register_invalid_email(self, client: AsyncClient):
        """Should reject invalid email format"""
        response = await client.post(
            "/api/v2/auth/register",
            json={
                "email": "not-an-email",
                "password": "password123"
            }
        )

        assert response.status_code == 422

    async def test_register_short_password(self, client: AsyncClient):
        """Should reject short password"""
        response = await client.post(
            "/api/v2/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "short"
            }
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    """Tests for /api/v2/auth/login endpoint"""

    async def test_login_success(self, client: AsyncClient, test_user):
        """Should login successfully with correct credentials"""
        response = await client.post(
            "/api/v2/auth/login",
            json={
                "email": test_user.email,
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Should reject wrong password"""
        response = await client.post(
            "/api/v2/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Should reject nonexistent email"""
        response = await client.post(
            "/api/v2/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestMe:
    """Tests for /api/v2/auth/me endpoint"""

    async def test_me_authenticated(self, client: AsyncClient, test_user, auth_headers):
        """Should return current user info"""
        response = await client.get("/api/v2/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id

    async def test_me_unauthenticated(self, client: AsyncClient):
        """Should reject unauthenticated request"""
        response = await client.get("/api/v2/auth/me")

        assert response.status_code == 401

    async def test_me_invalid_token(self, client: AsyncClient):
        """Should reject invalid token"""
        response = await client.get(
            "/api/v2/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestRefreshToken:
    """Tests for /api/v2/auth/refresh endpoint"""

    async def test_refresh_success(self, client: AsyncClient, test_user):
        """Should refresh tokens successfully"""
        # First login to get tokens
        login_response = await client.post(
            "/api/v2/auth/login",
            json={
                "email": test_user.email,
                "password": "password123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh tokens
        response = await client.post(
            "/api/v2/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Should reject invalid refresh token"""
        response = await client.post(
            "/api/v2/auth/refresh",
            json={"refresh_token": "invalid-token"}
        )

        assert response.status_code == 401
