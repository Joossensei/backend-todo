# app/api/v1/endpoints/token.py
from aiohttp import web
from app.services.auth_service import AuthService
from app.database import get_db
from app.schemas.token import Token
from app.schemas.user import UserLogin


def setup_routes(app: web.Application, cors, prefix: str):
    """Setup token routes."""

    # Login endpoint
    async def login_handler(request: web.Request):
        """Login and get access token."""
        try:
            data = await request.json()
            user_login = UserLogin(**data)

            async with get_db() as connection:
                token = await AuthService.authenticate(
                    connection, user_login.username, user_login.password
                )
                if not token:
                    return web.json_response(
                        {"detail": "Incorrect username or password"}, status=401
                    )

                return web.json_response(
                    Token(access_token=token, token_type="bearer").model_dump()
                )

        except Exception as e:
            return web.json_response(
                {"detail": f"Internal server error: {str(e)}"}, status=500
            )

    # Add routes
    app.router.add_post(f"{prefix}/token", login_handler)

    # Setup CORS for all routes
    for route in app.router.routes():
        if route.resource.canonical.startswith(f"{prefix}/token"):
            cors.add(route)
