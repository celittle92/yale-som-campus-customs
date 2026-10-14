"""Server-side sessions.

The browser holds a random opaque token in an HttpOnly cookie and nothing else. No
password, no hash, and no user data crosses the wire as a credential — the token is only
useful as a key into this process.

The store is in memory, so sessions end when the server restarts. That is honest for a
coursework app; a real deployment would use a shared store with expiry.

Note this does not contradict the signed-out decision (D2 in output/harness.md): the
cookie exists only once someone has chosen to log in. A signed-out visitor is never
given one, and is never tracked by cookie, IP, or fingerprint.
"""
from __future__ import annotations

import secrets

COOKIE_NAME = "campus_customs_session"

_sessions: dict[str, int] = {}


def create(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    _sessions[token] = user_id
    return token


def user_id_for(token: str | None) -> int | None:
    if not token:
        return None
    return _sessions.get(token)


def destroy(token: str | None) -> None:
    if token:
        _sessions.pop(token, None)
