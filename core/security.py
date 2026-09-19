from cryptography.fernet import Fernet
import base64
import hashlib
from core.config import settings


def _get_fernet_key() -> bytes:
    """Ensure key is valid 32-byte base64 encoded Fernet key."""
    key = settings.encryption_key.encode('utf-8')
    try:
        Fernet(key)
        return key
    except Exception:
        # Fallback to deriving 32 url-safe base64 bytes from settings string
        derived = base64.urlsafe_b64encode(hashlib.sha256(key).digest())
        return derived


def encrypt_api_key(raw_api_key: str) -> str:
    """Encrypt WB Supplier API key before saving to DB."""
    fernet = Fernet(_get_fernet_key())
    return fernet.encrypt(raw_api_key.encode('utf-8')).decode('utf-8')


def decrypt_api_key(encrypted_api_key: str) -> str:
    """Decrypt WB Supplier API key from DB."""
    fernet = Fernet(_get_fernet_key())
    return fernet.decrypt(encrypted_api_key.encode('utf-8')).decode('utf-8')
