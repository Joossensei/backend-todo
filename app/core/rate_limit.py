import time
import asyncio
from aiohttp import web
from collections import defaultdict
from typing import Dict, Tuple


class RateLimiter:
    def __init__(self):
        self.limits: Dict[str, Dict[str, Tuple[int, float]]] = defaultdict(dict)
        self.lock = asyncio.Lock()

    def _get_client_key(self, request: web.Request) -> str:
        """Get client key for rate limiting."""
        user = request.get("user", None)
        if user and hasattr(user, "key"):
            return f"user:{user.key}"

        # Get IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"

        peername = request.transport.get_extra_info("peername")
        if peername:
            return f"ip:{peername[0]}"

        return f"ip:{request.remote}"

    async def _check_rate_limit(self, key: str, limit_str: str) -> bool:
        """Check if request is within rate limit."""
        async with self.lock:
            current_time = time.time()

            # Parse limit string (e.g., "10/second;200/minute")
            limits = limit_str.split(";")

            for limit in limits:
                count, period = limit.split("/")
                count = int(count)

                if period == "second":
                    window = 1
                elif period == "minute":
                    window = 60
                elif period == "hour":
                    window = 3600
                else:
                    continue

                # Clean old entries
                if key in self.limits and limit in self.limits[key]:
                    last_count, last_time = self.limits[key][limit]
                    if current_time - last_time > window:
                        self.limits[key][limit] = (1, current_time)
                    elif last_count >= count:
                        return False
                    else:
                        self.limits[key][limit] = (last_count + 1, last_time)
                else:
                    self.limits[key][limit] = (1, current_time)

            return True

    def limit(self, limit_str: str):
        """Decorator for rate limiting endpoints."""

        def decorator(handler):
            async def wrapper(request: web.Request):
                key = self._get_client_key(request)
                if await self._check_rate_limit(key, limit_str):
                    return await handler(request)
                else:
                    return web.json_response(
                        {"error": "Rate limit exceeded"}, status=429
                    )

            return wrapper

        return decorator

    @web.middleware
    async def middleware(self, request: web.Request, handler):
        """Middleware for rate limiting."""
        # Check if endpoint has rate limiting
        if hasattr(handler, "__rate_limit__"):
            key = self._get_client_key(request)
            if not await self._check_rate_limit(key, handler.__rate_limit__):
                return web.json_response({"error": "Rate limit exceeded"}, status=429)

        return await handler(request)
