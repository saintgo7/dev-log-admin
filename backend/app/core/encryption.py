"""
Token encryption utilities using Fernet symmetric encryption
"""
import base64
import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


class TokenEncryption:
    """
    Encrypt and decrypt tokens using Fernet symmetric encryption.
    Uses GITHUB_TOKEN_ENCRYPTION_KEY from settings or generates a key from SECRET_KEY.
    """

    _instance: Optional["TokenEncryption"] = None
    _fernet: Optional[Fernet] = None

    def __new__(cls) -> "TokenEncryption":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize Fernet with encryption key"""
        key = settings.GITHUB_TOKEN_ENCRYPTION_KEY
        if not key:
            # Derive a key from SECRET_KEY if not explicitly set
            # This ensures consistency across restarts
            secret_bytes = settings.SECRET_KEY.encode()
            # Pad or truncate to 32 bytes and encode as base64
            key_bytes = (secret_bytes * 2)[:32]
            key = base64.urlsafe_b64encode(key_bytes).decode()

        self._fernet = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt(self, data: str) -> str:
        """
        Encrypt a string token.

        Args:
            data: Plain text token to encrypt

        Returns:
            Encrypted token as base64 string
        """
        if not data:
            return ""
        encrypted = self._fernet.encrypt(data.encode())
        return encrypted.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt an encrypted token.

        Args:
            encrypted_data: Encrypted token string

        Returns:
            Decrypted plain text token

        Raises:
            ValueError: If decryption fails
        """
        if not encrypted_data:
            return ""
        try:
            decrypted = self._fernet.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except InvalidToken as e:
            raise ValueError(f"Failed to decrypt token: {e}")


def get_token_encryption() -> TokenEncryption:
    """Get singleton TokenEncryption instance"""
    return TokenEncryption()


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.
    Use this to generate a key for GITHUB_TOKEN_ENCRYPTION_KEY.

    Returns:
        Base64-encoded Fernet key
    """
    return Fernet.generate_key().decode()
