from aiohttp import web
from app.core.config import settings
from app.services.auth_service import AuthService
from datetime import datetime, timedelta, timezone
from app.schemas.token import Token
from app.core.errors import AppError, UnauthorizedError, NotFoundError, ValidationError
import pydantic
import logging

logger = logging.getLogger(__name__)


async def login_for_access_token(request: web.Request) -> web.Response:
    db = request["conn"]
    form_data = await request.post()
    try:
        user = await AuthService.authenticate_user(
            db, form_data["username"], form_data["password"]
        )
        if not user:
            raise UnauthorizedError(ValueError("Incorrect username or password"))
        access_token_expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        access_token = AuthService.create_access_token(
            data={
                "sub": user["username"],
                "uid": user["key"],  # Add uid claim for rate limiting
            },
            expires_delta=access_token_expires,
        )
        return web.json_response(
            Token(
                access_token=access_token,
                token_type="bearer",
                expires_at=datetime.now(timezone.utc) + access_token_expires,
                user_key=user["key"],
            ).model_dump(),
            status=200,
        )
    except UnauthorizedError as e:
        logger.error(f"Unauthorized error: {e}")
        raise UnauthorizedError(e)
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e.custom_message}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error getting token: {e}")
        raise AppError(e)
