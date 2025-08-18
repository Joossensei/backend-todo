"""
CORS middleware for AioHTTP application.

This module contains middleware functions for handling Cross-Origin Resource Sharing.
"""

import logging
from typing import Iterable, Set, Optional
from aiohttp import web

logger = logging.getLogger(__name__)


def make_cors_middleware(
    allowed_origins: Iterable[str],
    allow_credentials: bool = False,
    strict_block: bool = True,  # 403 if Origin present but not allowed
    exposed_headers: Optional[Iterable[str]] = None,
):
    """
    Create a CORS middleware factory.

    Args:
        allowed_origins: Set of allowed origins
        allow_credentials: Whether to allow credentials
        strict_block: Whether to block requests with non-allowed origins
        exposed_headers: Headers to expose to the client
    """
    allowed: Set[str] = set(allowed_origins)
    exposed = ", ".join(exposed_headers or [])

    @web.middleware
    async def cors_middleware(request: web.Request, handler):
        origin = request.headers.get("Origin")

        # No Origin = no CORS (server-to-server or curl). Let through.
        if not origin:
            return await handler(request)

        # Origin present: check whitelist
        if origin not in allowed:
            if strict_block:
                return web.json_response(
                    {"detail": "CORS origin not allowed"}, status=403
                )
            # Not strict: treat as non-CORS
            return await handler(request)

        # Preflight (OPTIONS + Access-Control-Request-Method)
        if (
            request.method == "OPTIONS"
            and "Access-Control-Request-Method" in request.headers
        ):
            acrm = request.headers.get("Access-Control-Request-Method", "")
            acrh = request.headers.get("Access-Control-Request-Headers", "")
            headers = {
                "Access-Control-Allow-Origin": origin,
                "Vary": "Origin",
                "Access-Control-Allow-Methods": acrm
                or "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": acrh or "Authorization, Content-Type",
                "Access-Control-Max-Age": "600",
            }
            if allow_credentials:
                headers["Access-Control-Allow-Credentials"] = "true"
            if exposed:
                headers["Access-Control-Expose-Headers"] = exposed
            return web.Response(status=204, headers=headers)

        # "Regular" CORS request: let through and append headers
        resp = await handler(request)
        # Only add if no CORS headers are already set
        resp.headers.setdefault("Access-Control-Allow-Origin", origin)
        resp.headers.setdefault("Vary", "Origin")
        if allow_credentials:
            resp.headers.setdefault("Access-Control-Allow-Credentials", "true")
        if exposed:
            resp.headers.setdefault("Access-Control-Expose-Headers", exposed)
        return resp

    return cors_middleware


def _apply_cors(request: web.Request, response: web.StreamResponse) -> None:
    """
    Apply CORS headers to a response.

    This is a helper function used by other middleware to apply CORS headers
    to error responses.
    """
    allowed = {
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    }

    origin = request.headers.get("Origin")
    # Choose: strict whitelist or wildcard. With credentials you can't use '*'.
    if origin in allowed:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"  # important for caches
        response.headers["Access-Control-Allow-Credentials"] = "true"
        # Adjust to your front-end needs:
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        )
        response.headers["Access-Control-Expose-Headers"] = (
            "Content-Length, Content-Type"
        )
    else:
        # Or leave out for even stricter policy
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = "*"
