# app/api/v1/endpoints/user.py
from aiohttp import web
from app.services.user_service import UserService
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.api.deps import get_current_active_user


def setup_routes(app: web.Application, cors, prefix: str):
    """Setup user routes."""

    # Create user (register)
    async def create_user_handler(request: web.Request):
        """Create a new user."""
        try:
            data = await request.json()
            user_create = UserCreate(**data)

            pool = await get_db()
            async with pool.acquire() as connection:
                user = await UserService.create_user(connection, user_create)
                return web.json_response(UserResponse(**user).dict(), status=201)

        except ValueError as e:
            return web.json_response({"detail": str(e)}, status=400)
        except Exception as e:
            return web.json_response(
                {"detail": f"Internal server error: {str(e)}"}, status=500
            )

    # Get current user
    async def get_current_user_handler(request: web.Request):
        """Get current user information."""
        try:
            current_user = await get_current_active_user(request)
            return web.json_response(UserResponse(**current_user.__dict__).dict())

        except Exception as e:
            return web.json_response(
                {"detail": f"Internal server error: {str(e)}"}, status=500
            )

    # Add routes
    app.router.add_post(f"{prefix}", create_user_handler)
    app.router.add_get(f"{prefix}/me", get_current_user_handler)

    # Setup CORS for all routes
    for route in app.router.routes():
        if route.resource.canonical.startswith(prefix):
            cors.add(route)
