"""
Rate limiting middleware for AioHTTP application.

This module implements a sliding window rate limiter with multi-window policies.
Supports both per-user (JWT) and per-IP rate limiting with proper headers.
"""

import time
import os
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional
from aiohttp import web
from dataclasses import dataclass


@dataclass
class RateLimitWindow:
    """Represents a rate limit window configuration."""

    limit: int
    window_seconds: int


@dataclass
class RateLimitPolicy:
    """Represents a rate limit policy for a route."""

    method: str
    path: str
    keying_basis: str  # 'user' or 'ip'
    windows: List[RateLimitWindow]


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter."""

    def __init__(self):
        self._windows: Dict[str, deque] = defaultdict(deque)

    def _get_key(self, policy_key: str, identity: str) -> str:
        """Generate a unique key for the policy-identity combination."""
        return f"{policy_key}:{identity}"

    def _clean_old_entries(self, window_key: str, window_seconds: int):
        """Remove entries older than the window."""
        current_time = time.time()
        cutoff_time = current_time - window_seconds

        # Get the deque for this window
        window_deque = self._windows[window_key]

        # Remove old entries
        while window_deque and window_deque[0] < cutoff_time:
            window_deque.popleft()

    def check_rate_limit(
        self, policy_key: str, identity: str, windows: List[RateLimitWindow]
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Check if the request is within rate limits.

        Returns:
            Tuple of (allowed, window_info) where window_info contains
            limit, remaining, and reset time for each window.
        """
        current_time = time.time()
        window_info = {}

        for i, window in enumerate(windows):
            window_key = f"{policy_key}:{identity}:{i}"
            self._clean_old_entries(window_key, window.window_seconds)

            # Get the deque for this window
            window_deque = self._windows[window_key]

            # Count current requests in window
            current_count = len(window_deque)

            # Check if limit exceeded
            if current_count >= window.limit:
                # Calculate reset time (when oldest entry expires)
                if window_deque:
                    reset_time = int(window_deque[0] + window.window_seconds)
                else:
                    reset_time = int(current_time + window.window_seconds)

                window_info[f"window_{i}"] = {
                    "limit": window.limit,
                    "remaining": 0,
                    "reset": reset_time,
                }
                return False, window_info

            # Calculate reset time
            if window_deque:
                reset_time = int(window_deque[0] + window.window_seconds)
            else:
                reset_time = int(current_time + window.window_seconds)

            window_info[f"window_{i}"] = {
                "limit": window.limit,
                "remaining": window.limit - current_count,
                "reset": reset_time,
            }

        return True, window_info

    def record_request(
        self, policy_key: str, identity: str, windows: List[RateLimitWindow]
    ):
        """Record a request for rate limiting."""
        current_time = time.time()

        for i, window in enumerate(windows):
            window_key = f"{policy_key}:{identity}:{i}"
            window_deque = self._windows[window_key]
            window_deque.append(current_time)

    def reset_all(self):
        """Reset all rate limiters - useful for testing."""
        self._windows.clear()


# Global rate limiter instance
_rate_limiter = SlidingWindowRateLimiter()


def reset_rate_limiters():
    """Reset all rate limiters - useful for testing."""
    _rate_limiter.reset_all()


# Rate limit policies based on README.md table
RATE_LIMIT_POLICIES = [
    # Public endpoints - IP based
    RateLimitPolicy("GET", "/", "ip", [RateLimitWindow(60, 60)]),  # 60 per minute
    RateLimitPolicy("GET", "/health", "ip", [RateLimitWindow(60, 60)]),  # 60 per minute
    # Token endpoint - IP based with multi-window
    RateLimitPolicy(
        "POST",
        "/api/v1/token",
        "ip",
        [
            RateLimitWindow(5, 60),  # 5 per minute
            RateLimitWindow(100, 3600),  # 100 per hour
        ],
    ),
    # User endpoints - User key based
    RateLimitPolicy(
        "GET",
        "/api/v1/users",
        "user",
        [
            RateLimitWindow(10, 1),  # 10 per second
            RateLimitWindow(200, 60),  # 200 per minute
        ],
    ),
    RateLimitPolicy(
        "GET",
        "/api/v1/user/{key}",
        "user",
        [
            RateLimitWindow(20, 1),  # 20 per second
            RateLimitWindow(400, 60),  # 400 per minute
        ],
    ),
    RateLimitPolicy(
        "POST",
        "/api/v1/users",
        "ip",
        [
            RateLimitWindow(5, 60),  # 5 per minute
            RateLimitWindow(50, 3600),  # 50 per hour
        ],
    ),
    RateLimitPolicy(
        "PUT",
        "/api/v1/user/{key}",
        "user",
        [
            RateLimitWindow(10, 60),  # 10 per minute
            RateLimitWindow(100, 3600),  # 100 per hour
        ],
    ),
    RateLimitPolicy(
        "PUT",
        "/api/v1/user/{key}/password",
        "user",
        [
            RateLimitWindow(10, 60),  # 10 per minute
            RateLimitWindow(100, 3600),  # 100 per hour
        ],
    ),
    RateLimitPolicy(
        "DELETE",
        "/api/v1/user/{key}",
        "user",
        [
            RateLimitWindow(10, 60),  # 10 per minute
            RateLimitWindow(50, 3600),  # 50 per hour
        ],
    ),
    # Todo endpoints - User key based
    RateLimitPolicy(
        "GET",
        "/api/v1/todos",
        "user",
        [
            RateLimitWindow(10, 1),  # 10 per second
            RateLimitWindow(200, 60),  # 200 per minute
        ],
    ),
    RateLimitPolicy(
        "GET",
        "/api/v1/todo/{key}",
        "user",
        [
            RateLimitWindow(20, 1),  # 20 per second
            RateLimitWindow(400, 60),  # 400 per minute
        ],
    ),
    RateLimitPolicy(
        "POST",
        "/api/v1/todos",
        "user",
        [
            RateLimitWindow(10, 60),  # 10 per minute
            RateLimitWindow(100, 3600),  # 100 per hour
        ],
    ),
    RateLimitPolicy(
        "PUT",
        "/api/v1/todo/{key}",
        "user",
        [
            RateLimitWindow(20, 60),  # 20 per minute
            RateLimitWindow(200, 3600),  # 200 per hour
        ],
    ),
    RateLimitPolicy(
        "PATCH",
        "/api/v1/todo/{key}",
        "user",
        [
            RateLimitWindow(20, 60),  # 20 per minute
            RateLimitWindow(200, 3600),  # 200 per hour
        ],
    ),
    RateLimitPolicy(
        "DELETE",
        "/api/v1/todo/{key}",
        "user",
        [
            RateLimitWindow(10, 60),  # 10 per minute
            RateLimitWindow(50, 3600),  # 50 per hour
        ],
    ),
    # Priority endpoints - User key based
    RateLimitPolicy(
        "GET",
        "/api/v1/priorities",
        "user",
        [
            RateLimitWindow(10, 1),  # 10 per second
            RateLimitWindow(200, 60),  # 200 per minute
        ],
    ),
    RateLimitPolicy(
        "GET",
        "/api/v1/priority/{key}",
        "user",
        [
            RateLimitWindow(20, 1),  # 20 per second
            RateLimitWindow(400, 60),  # 400 per minute
        ],
    ),
    RateLimitPolicy(
        "POST",
        "/api/v1/priorities",
        "user",
        [
            RateLimitWindow(10, 60),  # 10 per minute
            RateLimitWindow(100, 3600),  # 100 per hour
        ],
    ),
    RateLimitPolicy(
        "PUT",
        "/api/v1/priority/{key}",
        "user",
        [
            RateLimitWindow(20, 60),  # 20 per minute
            RateLimitWindow(200, 3600),  # 200 per hour
        ],
    ),
    RateLimitPolicy(
        "PATCH",
        "/api/v1/priority/{key}",
        "user",
        [
            RateLimitWindow(20, 60),  # 20 per minute
            RateLimitWindow(200, 3600),  # 200 per hour
        ],
    ),
    RateLimitPolicy(
        "DELETE",
        "/api/v1/priority/{key}",
        "user",
        [
            RateLimitWindow(10, 60),  # 10 per minute
            RateLimitWindow(50, 3600),  # 50 per hour
        ],
    ),
]


def _get_client_ip(request: web.Request) -> str:
    """Extract client IP address from request."""
    # Check if we should trust proxy headers
    trust_proxy = os.getenv("TRUST_PROXY_IP_HEADERS", "false").lower() == "true"

    if trust_proxy:
        # Check X-Forwarded-For header
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (client IP)
            return forwarded_for.split(",")[0].strip()

        # Check Forwarded header
        forwarded = request.headers.get("Forwarded")
        if forwarded:
            # Parse Forwarded header for client IP
            for part in forwarded.split(","):
                part = part.strip()
                if part.startswith("for="):
                    ip = part[4:].strip('"')
                    return ip

    # Fallback to remote address
    return request.remote


def _get_canonical_path(request: web.Request) -> str:
    """Get canonical path for route matching."""
    if hasattr(request, "match_info") and request.match_info.route:
        resource = request.match_info.route.resource
        if hasattr(resource, "canonical"):
            return resource.canonical
    return request.path


def _find_matching_policy(request: web.Request) -> Optional[RateLimitPolicy]:
    """Find matching rate limit policy for the request."""
    method = request.method
    path = _get_canonical_path(request)

    for policy in RATE_LIMIT_POLICIES:
        if policy.method == method and policy.path == path:
            return policy

    return None


def _get_identity_key(request: web.Request, policy: RateLimitPolicy) -> str:
    """Get identity key for rate limiting based on policy."""
    if policy.keying_basis == "user":
        user_key = request.get("user_key")
        if user_key:
            return f"user:{user_key}"
        # Fallback to IP if no user key available
        return f"ip:{_get_client_ip(request)}"
    else:
        return f"ip:{_get_client_ip(request)}"


def _create_rate_limit_headers(
    window_info: Dict[str, Dict[str, int]],
) -> Dict[str, str]:
    """Create rate limit headers from window info."""
    headers = {}

    # Use the most restrictive window for the main headers
    most_restrictive = min(window_info.values(), key=lambda x: x["remaining"])

    headers["X-RateLimit-Limit"] = str(most_restrictive["limit"])
    headers["X-RateLimit-Remaining"] = str(most_restrictive["remaining"])
    headers["X-RateLimit-Reset"] = str(most_restrictive["reset"])

    return headers


@web.middleware
async def rate_limit_middleware(request: web.Request, handler):
    """Rate limiting middleware with sliding window and multi-window support."""
    # Find matching policy
    policy = _find_matching_policy(request)
    if not policy:
        return await handler(request)

    # Get identity key
    identity = _get_identity_key(request, policy)
    policy_key = f"{policy.method}:{policy.path}"

    # Check rate limits
    allowed, window_info = _rate_limiter.check_rate_limit(
        policy_key, identity, policy.windows
    )

    if not allowed:
        # Rate limit exceeded
        headers = _create_rate_limit_headers(window_info)

        # Find the window with the earliest reset time for Retry-After
        earliest_reset = min(w["reset"] for w in window_info.values())
        retry_after = max(1, earliest_reset - int(time.time()))
        headers["Retry-After"] = str(retry_after)

        return web.json_response(
            {"error": {"code": "rate_limited", "message": "Too Many Requests"}},
            status=429,
            headers=headers,
        )

    # Record the request
    _rate_limiter.record_request(policy_key, identity, policy.windows)

    # Add rate limit headers to response
    response = await handler(request)
    headers = _create_rate_limit_headers(window_info)

    # Update response headers
    for key, value in headers.items():
        response.headers[key] = value

    return response
