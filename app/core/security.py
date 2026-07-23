"""Authentication primitives: JWT verification and API-key checking.

Provides functions to create, verify, and resolve authentication credentials.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationError


# Create JWT access token
def create_access_token(
    subject: str, *, expires_minutes: int = 60, extra_claims: dict | None = None
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


# Verify and decode JWT token
def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired token.") from exc


# Validate API key
def verify_api_key(candidate: str | None) -> bool:
    """Constant-shape comparison used as a fallback/service-to-service auth path."""
    if not candidate:
        return False
    return candidate == settings.api_key


# Resolve user identity from credentials
def resolve_identity(
    authorization_header: str | None, api_key_header: str | None
) -> dict[str, Any]:
    """Resolve caller identity from either a Bearer JWT or a static API key.

    Returns a dict describing the authenticated principal. Raises
    AuthenticationError if neither credential is valid.
    """

    # Check JWT Bearer token
    if authorization_header and authorization_header.lower().startswith("bearer "):
        token = authorization_header.split(" ", 1)[1].strip()

        # Get user claims from token
        claims = decode_access_token(token)
        return {"type": "user", "subject": claims.get("sub"), "claims": claims}

    # Check API key authentication
    if verify_api_key(api_key_header):
        return {"type": "service", "subject": "api-key-client", "claims": {}}

    # No valid authentication found
    raise AuthenticationError("Missing or invalid credentials.")
