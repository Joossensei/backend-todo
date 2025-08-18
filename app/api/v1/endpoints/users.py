from aiohttp import web
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.schemas.user import UserResponse, UserListResponse
from app.utils.mapping import record_to_dict
from app.utils.pagination import build_pagination_link
from app.core.errors import AppError, NotFoundError, UnauthorizedError
import logging


logger = logging.getLogger(__name__)


async def read_users(request: web.Request):
    db = request["conn"]
    page = int(request.query.get("page", 1))
    size = int(request.query.get("size", 10))
    if size > 100:
        raise web.HTTPBadRequest(text="Size cannot be greater than 100")
    if page < 1:
        raise web.HTTPBadRequest(text="Page cannot be less than 1")
    try:
        skip = (page - 1) * size
        users = await UserService.get_users(db, skip, size)
        total = await UserService.get_total_users(db)
        users_list = [UserResponse(**record_to_dict(user)) for user in users]
        return web.json_response(
            UserListResponse(
                users=users_list,
                total=total,
                page=page,
                size=size,
                success=True,
                next_link=build_pagination_link(request.url, page + 1, size, total),
                prev_link=build_pagination_link(request.url, page - 1, size, total),
            ).model_dump(),
            status=200,
        )
    except Exception as e:
        raise AppError(e)


async def read_user(request: web.Request):
    db = request["conn"]
    key = request.match_info["key"]
    try:
        user = await UserService.get_user_by_key(db, key)
        if not user:
            raise NotFoundError(ValueError(f"User with key {key} not found"))
        return web.json_response(
            UserResponse(**record_to_dict(user)).model_dump(),
            status=200,
        )
    except Exception as e:
        raise AppError(e)


async def create_user(request: web.Request):
    db = request["conn"]
    user_in = await request.json()
    try:
        # Ensure username is unique
        existing_user = await UserService.get_user_by_username(db, user_in.username)
        if existing_user:
            raise AppError(ValueError("Username already exists"))
        db_user = await UserService.create_user(db, user_in)
        return web.json_response(
            UserResponse(**record_to_dict(db_user)).model_dump(),
            status=201,
        )
    except Exception as e:
        raise AppError(e)


async def update_user(
    request: web.Request,
    key: str,
):
    db = request["conn"]
    user_in = await request.json()
    try:
        # Check if the user is the current user
        current_user = await AuthService.get_user(db, request["user"])
        if not current_user:
            raise NotFoundError(ValueError("User not found"))
        if current_user.key != key:
            raise UnauthorizedError(
                ValueError("You are not allowed to update this user")
            )
        user = await UserService.update_user(db, key, user_in)
        return web.json_response(
            UserResponse(**record_to_dict(user)).model_dump(),
            status=200,
        )
    except Exception as e:
        raise AppError(e)


async def update_user_password(
    request: web.Request,
):
    db = request["conn"]
    user_key = request.match_info["key"]
    try:
        # Check if the user is the current user
        current_user = await AuthService.get_user(
            request,
            request.headers.get("Authorization").split(" ")[1],
            db,
        )
        if not current_user:
            raise NotFoundError(ValueError("User not found"))
        if current_user.key != user_key:
            raise UnauthorizedError(
                ValueError("You are not allowed to update this user")
            )
        # Update the user password
        user_in = await request.json()
        user = await UserService.update_user_password(db, user_key, user_in)
        return web.json_response(
            UserResponse(**record_to_dict(user)).model_dump(),
            status=200,
        )
    except Exception as e:
        raise AppError(e)


async def delete_user(
    request: web.Request,
    key: str,
):
    db = request["conn"]
    try:
        # Check if the user is the current user
        current_user = await AuthService.get_user(db, request["user"])
        if not current_user:
            raise NotFoundError(ValueError("User not found"))
        if current_user.key != key:
            raise UnauthorizedError(
                ValueError("You are not allowed to delete this user")
            )
        # Delete the user
        user = await UserService.get_user_by_key(db, key)
        if not user:
            raise NotFoundError(ValueError(f"User with key {key} not found"))
        await UserService.delete_user(db, key)
        return web.Response(status=204)
    except Exception as e:
        raise AppError(e)
