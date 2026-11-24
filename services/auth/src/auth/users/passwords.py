"""Password hashing with argon2 (RNF-02, docs/06 D1.3)."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_hasher = PasswordHasher()

# Verified when the email does not exist, so a wrong email takes as long as a
# wrong password: the response time does not reveal which emails exist.
_DUMMY_HASH = _hasher.hash("not-a-real-password")

MIN_LENGTH = 12


def hash_password(password: str) -> str:
    """Return the argon2 hash to store; the password itself is never stored."""
    return _hasher.hash(password)


def verify(password_hash: str | None, password: str) -> bool:
    """Check a password against its hash; with no hash, spend the same time and fail."""
    try:
        return _hasher.verify(password_hash or _DUMMY_HASH, password) and password_hash is not None
    except (VerificationError, InvalidHashError):
        return False


def needs_rehash(password_hash: str) -> bool:
    """Tell whether the hash uses old parameters and should be recomputed at the next login."""
    return _hasher.check_needs_rehash(password_hash)
