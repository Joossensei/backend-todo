from aiohttp import web
from app.core.security import TokenManager
from app.models.user import User as UserModel
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

    # Get database connection
    pool = await get_db()
    async with pool.acquire() as connection:
        # Query user from database
        user_data = await connection.fetchrow(
            "SELECT * FROM users WHERE username = $1", username
        )

        if not user_data:
            raise web.HTTPUnauthorized(
                text=json.dumps({"detail": "Invalid credentials"})
            )

        # Create user object
        user = UserModel(
            id=user_data["id"],
            key=user_data["key"],
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=user_data["hashed_password"],
            is_active=user_data["is_active"],
            created_at=user_data["created_at"],
            updated_at=user_data["updated_at"],
        )

        # Add user to request
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
