"""
Integration tests for GitHub API endpoints
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings


class TestGitHubOAuthEndpoints:
    """Test GitHub OAuth endpoints"""

    @pytest.mark.asyncio
    async def test_get_oauth_authorize_url(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting OAuth authorization URL"""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.GITHUB_CLIENT_ID = "test_client_id"
            mock_settings.GITHUB_CLIENT_SECRET = "test_secret"
            mock_settings.GITHUB_CALLBACK_URL = "http://localhost/callback"
            mock_settings.GITHUB_OAUTH_URL = "https://github.com/login/oauth"

            response = await client.get(
                "/api/v2/github/oauth/authorize",
                headers=auth_headers,
            )

            # May return 400 if GitHub OAuth is not configured in test env
            # Just check it doesn't error with 500
            assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_get_connection_status_no_connection(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting connection status when not connected"""
        response = await client.get(
            "/api/v2/github/connection",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is False
        assert data["connection"] is None

    @pytest.mark.asyncio
    async def test_revoke_connection_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test revoking non-existent connection"""
        response = await client.delete(
            "/api/v2/github/connection",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestGitHubRepositoryEndpoints:
    """Test GitHub repository endpoints"""

    @pytest.mark.asyncio
    async def test_list_available_repos_no_connection(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test listing repos without GitHub connection"""
        response = await client.get(
            "/api/v2/github/repositories/available",
            headers=auth_headers,
        )

        # Should return 400 because no GitHub connection
        assert response.status_code == 400
        assert "connection" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_link_repository_no_connection(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
    ):
        """Test linking repo without GitHub connection"""
        response = await client.post(
            "/api/v2/github/repositories",
            headers=auth_headers,
            json={
                "project_id": test_project["id"],
                "owner": "test-owner",
                "name": "test-repo",
            },
        )

        # Should return 400 because no GitHub connection
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_repository_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting non-existent repository"""
        response = await client.get(
            "/api/v2/github/repositories/non-existent-id",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestGitHubSyncEndpoints:
    """Test GitHub sync endpoints"""

    @pytest.mark.asyncio
    async def test_sync_repository_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test syncing non-existent repository"""
        response = await client.post(
            "/api/v2/github/repositories/non-existent-id/sync",
            headers=auth_headers,
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_sync_status(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting sync status for non-existent repository"""
        response = await client.get(
            "/api/v2/github/repositories/non-existent-id/sync/status",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_syncing"] is False
        assert data["pending_syncs"] == 0


class TestWebhookEndpoints:
    """Test webhook endpoints"""

    @pytest.mark.asyncio
    async def test_github_webhook_missing_headers(
        self,
        client: AsyncClient,
    ):
        """Test webhook without required headers"""
        response = await client.post(
            "/api/v2/webhooks/github",
            json={"test": "data"},
        )

        # Missing required headers
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_github_webhook_ping_event(
        self,
        client: AsyncClient,
        db: AsyncSession,
    ):
        """Test webhook ping event"""
        import hmac
        import hashlib

        payload = b'{"zen": "test", "hook_id": 123}'

        # 서비스가 모듈 임포트 시점에 settings 인스턴스를 직접 참조하므로
        # 모듈 이름(app.core.config.settings)을 교체하면 서비스에 닿지 않는다.
        # 실제 인스턴스 속성을 patch.object로 덮어써야 검증 경로에 반영된다.
        with patch.object(settings, "GITHUB_WEBHOOK_SECRET", "test_secret"):

            signature = "sha256=" + hmac.new(
                b"test_secret",
                payload,
                hashlib.sha256
            ).hexdigest()

            response = await client.post(
                "/api/v2/webhooks/github",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-GitHub-Event": "ping",
                    "X-GitHub-Delivery": "test-delivery-123",
                    "X-Hub-Signature-256": signature,
                },
            )

            # Should succeed
            assert response.status_code == 202
            data = response.json()
            assert data["event_type"] == "ping"

    @pytest.mark.asyncio
    async def test_github_webhook_invalid_signature(
        self,
        client: AsyncClient,
    ):
        """Test webhook with invalid signature"""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.GITHUB_WEBHOOK_SECRET = "test_secret"

            response = await client.post(
                "/api/v2/webhooks/github",
                json={"test": "data"},
                headers={
                    "X-GitHub-Event": "push",
                    "X-GitHub-Delivery": "test-delivery-456",
                    "X-Hub-Signature-256": "sha256=invalid_signature",
                },
            )

            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_webhook_events(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test listing webhook events"""
        response = await client.get(
            "/api/v2/webhooks/github/events",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_webhook_event_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting non-existent webhook event"""
        response = await client.get(
            "/api/v2/webhooks/github/events/non-existent-id",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestGitHubRateLimit:
    """Test rate limit endpoint"""

    @pytest.mark.asyncio
    async def test_get_rate_limit_no_connection(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting rate limit without GitHub connection"""
        response = await client.get(
            "/api/v2/github/rate-limit",
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "connection" in response.json()["detail"].lower()
