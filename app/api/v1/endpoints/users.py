from aiohttp import web
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserListResponse,
    UserUpdate,
    UserUpdatePassword,
)
from app.utils.mapping import record_to_dict
from app.utils.pagination import build_pagination_link, parse_pagination
from app.core.errors import AppError, NotFoundError, ValidationError, UnauthorizedError
import logging
from app.middleware.authentication import require_auth
from app.validators.user_validator import (
    UserCreateValidator,
    UserUpdateValidator,
    UserUpdatePasswordValidator,
)
import pydantic

logger = logging.getLogger(__name__)


@require_auth()
async def read_users(request: web.Request):
    db = request["conn"]
    page, size, skip = parse_pagination(
        request.query.get("page"), request.query.get("size")
    )
    try:
        users = await UserService.get_users(db, skip, size)
        total = await UserService.get_total_users(db)
        users_list = [UserResponse(**record_to_dict(user)) for user in users]
        return web.json_response(
            UserListResponse(
                users=users_list,
                total=total,
                page=page,
                size=len(users_list),
                success=True,
                next_link=build_pagination_link(request.url, page + 1, size, total),
                prev_link=build_pagination_link(request.url, page - 1, size, total),
            ).model_dump(),
            status=200,
        )
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise AppError(e)


@require_auth()
async def read_user(request: web.Request):
    db = request["conn"]
    key = request.match_info["key"]
    try:
        user = await UserService.get_user_by_key(db, key)
        if not user:
            raise NotFoundError(f"User with key {key} not found")
        return web.json_response(
            UserResponse(**record_to_dict(user)).model_dump(),
            status=200,
        )
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise AppError(e)


async def create_user(request: web.Request):
    db = request["conn"]
    user_in = await request.json()
    try:
        user_model = UserCreate(**user_in)
        user_model = await UserCreateValidator.validate_user(user_model, db)
        db_user = await UserService.create_user(db, user_model)
        return web.json_response(
            UserResponse(**record_to_dict(db_user)).model_dump(),
            status=201,
        )
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise AppError(e)


@require_auth()
async def update_user(
    request: web.Request,
):
    db = request["conn"]
    key = request.match_info["key"]
    user_in = await request.json()
    try:
        # Check if the user is the current user
        current_user = await AuthService.get_user(db, request["user"])
        if not current_user:
            raise NotFoundError("User not found")
        user_update = await UserService.get_user_by_key(db, key)
        if not user_update:
            raise NotFoundError(f"User with key {key} not found")
        if current_user["key"] != key:
            logger.error(
                f"User {current_user['key']} is not allowed to update user {key}"
            )
            raise ValidationError("You are not allowed to update this user")
        user_model = UserUpdate(**user_in)
        user_model = await UserUpdateValidator.validate_user(
            user_model, db, current_user["key"]
        )
        user = await UserService.update_user(db, key, user_model, current_user["key"])
        user_data = UserResponse(**record_to_dict(user)).model_dump()
        return web.json_response(
            user_data,
            status=200,
        )
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise AppError(e)


@require_auth()
async def patch_user(request: web.Request):
    db = request["conn"]
    key = request.match_info["key"]
    user_in = await request.json()
    try:
        user = await UserService.get_user_by_key(db, key)
        if not user:
            raise NotFoundError(f"User with key {key} not found")
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error patching user: {e}")
        raise AppError(e)
    try:
        user_model = UserUpdate(**user_in)
        user_model = await UserUpdateValidator.validate_user(user_model, db, key)
        user = await UserService.patch_user(db, key, user_model, request["user"])
        return web.json_response(
            UserResponse(**record_to_dict(user)).model_dump(),
            status=200,
        )
    except UnauthorizedError as e:
        logger.error(f"Unauthorized error: {e}")
        raise UnauthorizedError(e)
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error patching user: {e}")
        raise AppError(e)


@require_auth()
async def update_user_password(
    request: web.Request,
):
    db = request["conn"]
    user_key = request.match_info["key"]
    try:
        # Check if the user is the current user
        current_user = await AuthService.get_user(
            db,
            request["user"],
        )
        if not current_user:
            raise NotFoundError("User not found")
        if current_user["key"] != user_key:
            raise ValidationError("You are not allowed to update this user")
        # Update the user password
        user_in = await request.json()
        user_model = UserUpdatePassword(**user_in)
        user_model = await UserUpdatePasswordValidator.validate_user_password(
            user_model, db, current_user["key"]
        )
        await UserService.update_user_password(db, user_key, user_model)
        return web.json_response(
            {"success": True, "message": "User password updated successfully"},
            status=200,
        )
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e.custom_message}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Pydantic validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise AppError(e)


@require_auth()
async def delete_user(
    request: web.Request,
):
    db = request["conn"]
    key = request.match_info["key"]
    try:
        # Check if the user is the current user
        current_user = await AuthService.get_user(db, request["user"])
        if not current_user:
            raise NotFoundError("User not found")
        user = await UserService.get_user_by_key(db, key)
        if not user:
            raise NotFoundError(f"User with key {key} not found")
        if current_user["key"] != key:
            logger.error(
                f"User {current_user['key']} is not allowed to delete user {key}"
            )
            raise ValidationError("You are not allowed to delete this user")
        # Delete the user
        await UserService.delete_user(db, key)
        return web.Response(status=204)
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
        logger.error(f"Error updating user: {e}")
        raise AppError(e)
