"""
Unit tests for security module
"""
import pytest
from datetime import timedelta

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
    TokenExpiredError,
    InvalidTokenError
)


class TestPasswordHashing:
    """Tests for password hashing functions"""

    def test_hash_password_returns_string(self):
        """hash_password should return a string"""
        hashed = hash_password("mypassword")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_not_plain(self):
        """hash_password should not return plain password"""
        password = "mypassword"
        hashed = hash_password(password)
        assert hashed != password

    def test_hash_password_different_each_time(self):
        """hash_password should produce different hashes (salt)"""
        password = "mypassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """verify_password should return True for correct password"""
        password = "mypassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """verify_password should return False for wrong password"""
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False


class TestJWTTokens:
    """Tests for JWT token functions"""

    def test_create_access_token(self):
        """create_access_token should return a valid token"""
        token = create_access_token(subject="user123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """create_refresh_token should return a valid token"""
        token = create_refresh_token(subject="user123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_token_valid(self):
        """decode_token should decode valid token"""
        token = create_access_token(subject="user123")
        payload = decode_token(token)

        assert payload["sub"] == "user123"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_decode_token_invalid(self):
        """decode_token should raise for invalid token"""
        with pytest.raises(InvalidTokenError):
            decode_token("invalid-token")

    def test_decode_token_expired(self):
        """decode_token should raise for expired token"""
        token = create_access_token(
            subject="user123",
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        with pytest.raises(TokenExpiredError):
            decode_token(token)

    def test_verify_token_access(self):
        """verify_token should return subject for valid access token"""
        token = create_access_token(subject="user123")
        subject = verify_token(token, token_type="access")
        assert subject == "user123"

    def test_verify_token_refresh(self):
        """verify_token should return subject for valid refresh token"""
        token = create_refresh_token(subject="user123")
        subject = verify_token(token, token_type="refresh")
        assert subject == "user123"

    def test_verify_token_wrong_type(self):
        """verify_token should raise for wrong token type"""
        access_token = create_access_token(subject="user123")

        with pytest.raises(InvalidTokenError) as exc_info:
            verify_token(access_token, token_type="refresh")

        assert "Expected refresh token" in str(exc_info.value)

    def test_access_token_with_additional_claims(self):
        """create_access_token should include additional claims"""
        token = create_access_token(
            subject="user123",
            additional_claims={"email": "user@example.com", "role": "admin"}
        )
        payload = decode_token(token)

        assert payload["email"] == "user@example.com"
        assert payload["role"] == "admin"
