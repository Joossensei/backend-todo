from aiohttp import web
from app.core.config import settings
from app.services.auth_service import AuthService
from datetime import datetime, timedelta, timezone


async def login_for_access_token(
    request: web.Request,
) -> web.Response:
    db = request["conn"]
    form_data = await request.post()
    try:
        user = await AuthService.authenticate_user(
            db, form_data["username"], form_data["password"]
        )
        if not user:
            raise web.HTTPUnauthorized(
                text="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        access_token = AuthService.create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        return web.json_response(
            {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_at": (
                    datetime.now(timezone.utc) + access_token_expires
                ).isoformat(),
                "user_key": user["key"],
            }
        )
    except Exception as e:
        if isinstance(e, web.HTTPUnauthorized):
            raise e
        raise web.HTTPInternalServerError(
            text=f"Internal server error while logging in (original error message: {e})",
        )
