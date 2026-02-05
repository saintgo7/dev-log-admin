"""
Unit tests for GitHub integration
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.services.github_client_service import GitHubClient, GitHubAPIError
from app.services.webhook_service import WebhookService, WebhookSignatureError
from app.core.encryption import TokenEncryption, generate_encryption_key


class TestTokenEncryption:
    """Test token encryption utilities"""

    def test_encrypt_decrypt_roundtrip(self):
        """Test that encryption and decryption work correctly"""
        encryption = TokenEncryption()
        original = "ghp_test_token_12345"

        encrypted = encryption.encrypt(original)
        decrypted = encryption.decrypt(encrypted)

        assert decrypted == original
        assert encrypted != original  # Should be different from original

    def test_encrypt_empty_string(self):
        """Test encrypting empty string"""
        encryption = TokenEncryption()
        assert encryption.encrypt("") == ""
        assert encryption.decrypt("") == ""

    def test_decrypt_invalid_token(self):
        """Test decrypting invalid token raises error"""
        encryption = TokenEncryption()
        with pytest.raises(ValueError, match="Failed to decrypt"):
            encryption.decrypt("invalid_encrypted_data")

    def test_generate_encryption_key(self):
        """Test generating encryption key"""
        key = generate_encryption_key()
        assert len(key) == 44  # Fernet keys are 44 characters base64
        assert key.endswith("=")  # Base64 padding


class TestWebhookSignatureVerification:
    """Test webhook signature verification"""

    @pytest.fixture
    def webhook_service(self):
        """Create mock webhook service"""
        db = MagicMock()
        return WebhookService(db)

    def test_verify_valid_signature(self, webhook_service):
        """Test verifying valid signature"""
        import hmac
        import hashlib

        secret = "test_secret"
        payload = b'{"test": "data"}'

        # Generate valid signature
        signature = "sha256=" + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        result = webhook_service.verify_signature(payload, signature, secret)
        assert result is True

    def test_verify_invalid_signature(self, webhook_service):
        """Test verifying invalid signature"""
        with pytest.raises(WebhookSignatureError):
            webhook_service.verify_signature(
                b'{"test": "data"}',
                "sha256=invalid_signature",
                "test_secret"
            )

    def test_verify_missing_signature(self, webhook_service):
        """Test missing signature raises error when secret is set"""
        with pytest.raises(WebhookSignatureError, match="Missing signature"):
            webhook_service.verify_signature(b'{"test": "data"}', None, "test_secret")

    def test_verify_invalid_signature_format(self, webhook_service):
        """Test invalid signature format"""
        with pytest.raises(WebhookSignatureError, match="Invalid signature format"):
            webhook_service.verify_signature(
                b'{"test": "data"}',
                "sha1=abc123",  # Wrong algorithm prefix
                "test_secret"
            )


class TestGitHubClientParsing:
    """Test GitHub API response parsing"""

    def test_parse_commit_type_feat(self):
        """Test parsing feature commit type"""
        from app.services.webhook_service import WebhookService

        db = MagicMock()
        service = WebhookService(db)

        assert service._parse_commit_type("feat: add new feature") == "feat"
        assert service._parse_commit_type("feat(scope): add new feature") == "feat"

    def test_parse_commit_type_fix(self):
        """Test parsing fix commit type"""
        from app.services.webhook_service import WebhookService

        db = MagicMock()
        service = WebhookService(db)

        assert service._parse_commit_type("fix: resolve bug") == "fix"
        assert service._parse_commit_type("fix(api): resolve bug") == "fix"

    def test_parse_commit_type_various(self):
        """Test parsing various commit types"""
        from app.services.webhook_service import WebhookService

        db = MagicMock()
        service = WebhookService(db)

        assert service._parse_commit_type("docs: update readme") == "docs"
        assert service._parse_commit_type("refactor: clean up code") == "refactor"
        assert service._parse_commit_type("test: add unit tests") == "test"
        assert service._parse_commit_type("perf: improve performance") == "perf"
        assert service._parse_commit_type("style: format code") == "style"
        assert service._parse_commit_type("chore: update deps") == "chore"
        assert service._parse_commit_type("ci: update workflow") == "ci"
        assert service._parse_commit_type("build: update build") == "build"

    def test_parse_commit_type_default(self):
        """Test default commit type for non-conventional commits"""
        from app.services.webhook_service import WebhookService

        db = MagicMock()
        service = WebhookService(db)

        assert service._parse_commit_type("random commit message") == "chore"
        assert service._parse_commit_type("") == "chore"
        assert service._parse_commit_type("Update something") == "chore"


class TestGitHubClient:
    """Test GitHub API client"""

    @pytest.fixture
    def mock_response(self):
        """Create mock HTTP response"""
        response = MagicMock()
        response.status_code = 200
        response.is_success = True
        response.headers = {
            "X-RateLimit-Remaining": "4999",
            "X-RateLimit-Reset": "1609459200",
        }
        return response

    @pytest.mark.asyncio
    async def test_client_context_manager(self):
        """Test client context manager"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance

            async with GitHubClient("test_token") as client:
                assert client._client == mock_instance

            mock_instance.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, mock_response):
        """Test rate limit error handling"""
        mock_response.headers["X-RateLimit-Remaining"] = "0"
        mock_response.headers["X-RateLimit-Reset"] = str(int(datetime.now(timezone.utc).timestamp()) + 3600)

        # This would need more complex mocking to test fully
        # For now, just verify the error class exists
        from app.services.github_client_service import GitHubRateLimitError
        error = GitHubRateLimitError(datetime.now(timezone.utc))
        assert "rate limit exceeded" in str(error).lower()


class TestGitHubSchemas:
    """Test GitHub schema validation"""

    def test_github_oauth_request_defaults(self):
        """Test OAuth request default scopes"""
        from app.schemas.github import GitHubOAuthRequest

        request = GitHubOAuthRequest()
        assert request.scopes == ["repo", "read:user", "user:email"]

    def test_github_repository_create_validation(self):
        """Test repository create schema validation"""
        from app.schemas.github import GitHubRepositoryCreate

        repo = GitHubRepositoryCreate(
            project_id="test-uuid",
            owner="owner",
            name="repo"
        )
        assert repo.project_id == "test-uuid"
        assert repo.owner == "owner"
        assert repo.name == "repo"

    def test_sync_request_defaults(self):
        """Test sync request defaults"""
        from app.schemas.github import SyncRequest

        request = SyncRequest()
        assert request.sync_commits is True
        assert request.sync_issues is False
        assert request.sync_prs is False
        assert request.full_sync is False

    def test_webhook_event_response(self):
        """Test webhook event response"""
        from app.schemas.github import WebhookEventResponse

        event = WebhookEventResponse(
            id="test-id",
            event_type="push",
            delivery_id="delivery-123",
            processed=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        assert event.event_type == "push"
        assert event.processed is True
