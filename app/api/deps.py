from aiohttp import web
from app.core.security import TokenManager
from app.schemas.user import User as UserSchema
from app.database import get_db
import json


async def get_current_user_middleware(request: web.Request, handler):
    """Middleware to authenticate users and add user to request."""
    # Skip authentication for certain endpoints
    if request.path in ["/api/v1/token", "/api/v1/users"] and request.method == "POST":
        return await handler(request)

    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise web.HTTPUnauthorized(text=json.dumps({"detail": "Invalid token"}))

    token = auth_header.split(" ")[1]

    try:
        payload = TokenManager.decode(token)
    except Exception:
        raise web.HTTPUnauthorized(text=json.dumps({"detail": "Invalid token"}))

    username = payload.get("sub")
    if not username:
        raise web.HTTPUnauthorized(text=json.dumps({"detail": "Invalid credentials"}))

    async with get_db() as connection:
        user_data = await connection.fetchrow(
            "SELECT * FROM users WHERE username = $1", username
        )

        if not user_data:
            raise web.HTTPUnauthorized(
                text=json.dumps({"detail": "Invalid credentials"})
            )

        user = UserSchema(**dict(user_data))
        request["user"] = user
        return await handler(request)


async def get_current_active_user(request: web.Request):
    """Get current active user from request."""
    user = request.get("user")
    if not user:
        raise web.HTTPUnauthorized(text=json.dumps({"detail": "Not authenticated"}))

    if not user.is_active:
        raise web.HTTPBadRequest(text=json.dumps({"detail": "Inactive user"}))

    return user
