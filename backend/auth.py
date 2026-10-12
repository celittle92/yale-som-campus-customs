"""Password hashing for Campus Customs.

Signup and login **must** use identical settings, or a correct password will not match.
That is why there is exactly one module here and exactly one set of constants: both paths
call into this file, and `verify_password` takes the salt from the stored record rather
than inventing one.

Format, matching the seeded rows in the supplied database:

    pbkdf2_sha256$<salt>$<64 hex characters>

- PBKDF2-HMAC-SHA256
- 120,000 iterations (not stored in the string, so it is fixed here)
- a unique random salt per password, generated at signup only
- verification re-hashes the typed password and compares in constant time

The stored value is never reversed. There is no way to reverse it; that is the point.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000
SALT_BYTES = 16
SEPARATOR = "$"


def _derive(password: str, salt: str, iterations: int) -> str:
    """The one place a digest is computed. Both signup and login come through here."""
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    ).hex()


def hash_password(password: str) -> str:
    """Hash a new password with a fresh random salt. Used at signup only."""
    if not password:
        raise ValueError("password must not be empty")
    salt = secrets.token_hex(SALT_BYTES)
    digest = _derive(password, salt, ITERATIONS)
    return f"{ALGORITHM}{SEPARATOR}{salt}{SEPARATOR}{digest}"


def verify_password(password: str, stored: str) -> bool:
    """Check a typed password against a stored record.

    Reads the salt out of the middle of the stored string — it does not generate one —
    re-hashes with the same settings, and compares with `hmac.compare_digest` so the
    comparison takes the same time whether the first byte differs or the last.

    Returns False for anything malformed rather than raising, so a damaged row cannot
    turn a failed login into a 500 and reveal that the account exists.
    """
    if not password or not stored:
        return False
    parts = stored.split(SEPARATOR)
    if len(parts) != 3:
        return False
    algorithm, salt, expected = parts
    if algorithm != ALGORITHM or not salt or not expected:
        return False
    try:
        candidate = _derive(password, salt, ITERATIONS)
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(candidate, expected)
