# app/middleware/rate_limit.py
from aiohttp import web
from aiolimiter import AsyncLimiter

ENDPOINT_LIMITS = {
    "/": (60, 60),
    "/health": (60, 60),
    "/api/v1/token": (5, 60),
    "/api/v1/users": (10, 60),
    "/api/v1/user/{key}": (20, 60),
    "/api/v1/user/{key}/password": (10, 60),
    "/api/v1/todos": (10, 60),
    "/api/v1/todo/{key}": (20, 60),
    "/api/v1/priorities": (10, 60),
    "/api/v1/priority/{key}": (20, 60),
}

_limiters = {
    path: AsyncLimiter(rps, period) for path, (rps, period) in ENDPOINT_LIMITS.items()
}


@web.middleware
async def rate_limit_middleware(request: web.Request, handler):
    limiter = _limiters.get(request.path)
    if not limiter:
        return await handler(request)
    if not limiter.has_capacity():
        return web.json_response(
            {"error": {"code": "rate_limited", "message": "Too Many Requests"}},
            status=429,
            headers={"Retry-After": str(limiter.available_after)},
        )
    async with limiter:
        return await handler(request)
