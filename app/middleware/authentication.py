"""
Authentication middleware for AioHTTP application.

This module contains middleware functions for authentication and authorization.
"""

import functools
from typing import Iterable, Optional, Set, Dict, Any
from aiohttp import web
from app.core.security import TokenManager
import jwt


def _bearer_unauthorized(error: str, desc: str) -> web.Response:
    """Create an unauthorized response with proper Bearer token format."""
    hdr = f'Bearer realm="api", error="{error}", error_description="{desc}"'
    return web.json_response(
        {"detail": desc}, headers={"WWW-Authenticate": hdr}, status=401
    )


def _forbidden(desc: str) -> web.Response:
    """Create a forbidden response."""
    return web.json_response({"detail": desc}, status=403)


def _extract_bearer(request: web.Request) -> Optional[str]:
    """Extract Bearer token from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return auth[7:]  # Remove "Bearer " prefix


def _decode_jwt(token: str) -> Dict[str, Any]:
    """Decode and verify JWT token."""
    return TokenManager.decode(token)


def _scopes_from_claims(claims: Dict[str, Any]) -> Set[str]:
    """Extract scopes from JWT claims."""
    if "scope" in claims:
        return set(claims["scope"].split())
    if "scp" in claims:
        return set(claims["scp"])
    return set()


@web.middleware
async def auth_parsing_middleware(request: web.Request, handler):
    """
    Authentication parsing middleware.

    Parses and validates JWT tokens from Authorization headers.
    Sets user and claims in request for downstream handlers.
    """
    token = _extract_bearer(request)
    if token is None:
        # Public request; no user
        request["user"] = None
        request["claims"] = None
        return await handler(request)

    try:
        claims = _decode_jwt(token)
    except jwt.ExpiredSignatureError:
        return _bearer_unauthorized("invalid_token", "Token expired")
    except jwt.InvalidTokenError as e:
        return _bearer_unauthorized("invalid_token", str(e) or "Invalid token")

    # Store claims for downstream handlers/decorators
    request["claims"] = claims
    request["user"] = claims.get("sub")  # or 'preferred_username' depending on your IdP
    return await handler(request)


def require_auth(scopes: Optional[Iterable[str]] = None, any_scope: bool = False):
    """
    Decorator to enforce authentication and authorization on specific routes.

    Args:
        scopes: Required scopes for the endpoint
        any_scope: If True, any of the scopes is sufficient. If False, all scopes are required.
    """

    def decorator(handler):
        @functools.wraps(handler)
        async def wrapped(request: web.Request, *args, **kwargs):
            claims = request.get("claims")
            if not claims:
                return _bearer_unauthorized("invalid_token", "Missing or invalid token")

            if scopes:
                needed = set(scopes)
                have = _scopes_from_claims(claims)
                ok = bool(have & needed) if any_scope else needed.issubset(have)
                if not ok:
                    return _forbidden("Insufficient scope")

            return await handler(request, *args, **kwargs)

        return wrapped

    return decorator
