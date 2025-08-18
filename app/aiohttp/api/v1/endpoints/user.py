from aiohttp import web
from db.services.auth_service import AuthService
from main_aiohttp import routes
from db.services.user_service import UserService


@routes.get("/api/v1/users")
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
        users_list = []
        for user in users:
            users_list.append(
                {
                    "key": user["key"],
                    "username": user["username"],
                    "name": user["name"],
                    "email": user["email"],
                    "is_active": user["is_active"],
                    "created_at": user["created_at"].isoformat(),
                    "updated_at": (
                        user["updated_at"].isoformat() if user["updated_at"] else None
                    ),
                }
            )
        return web.json_response(
            {
                "users": users_list,
                "total": total,
                "page": page,
                "size": size,
                "success": True,
                "next_link": (
                    f"/api/v1/users?page={page + 1}&size={size}"
                    if page * size < total
                    else None
                ),
                "prev_link": (
                    f"/api/v1/users?page={page - 1}&size={size}" if page > 1 else None
                ),
            }
        )
    except Exception as e:
        if isinstance(e, web.HTTPException):
            raise e
        raise web.HTTPInternalServerError(
            text=f"Internal server error while getting users (original error message: {e})",
            detail=f"Internal server error while getting users (original error message: {e})",
        )


@routes.get(
    "/api/v1/users/{key}",
)
async def read_user(request: web.Request):
    db = request["conn"]
    key = request.match_info["key"]
    try:
        user = await UserService.get_user_by_key(db, key)
        if not user:
            raise web.HTTPNotFound(text=f"User with key {key} not found")
        return web.json_response(
            {
                "key": user["key"],
                "username": user["username"],
                "name": user["name"],
                "email": user["email"],
                "is_active": user["is_active"],
                "created_at": user["created_at"].isoformat(),
                "updated_at": (
                    user["updated_at"].isoformat() if user["updated_at"] else None
                ),
                "success": True,
            }
        )
    except Exception as e:
        if isinstance(e, web.HTTPException):
            raise e
        raise web.HTTPInternalServerError(
            text=f"Internal server error while getting user (original error message: {e})",
        )


@routes.post("/api/v1/users")
async def create_user(request: web.Request):
    db = request["conn"]
    user_in = await request.json()
    try:
        # Ensure username is unique
        existing_user = await UserService.get_user_by_username(db, user_in.username)
        if existing_user:
            raise web.HTTPBadRequest(text="Username already exists")
        db_user = await UserService.create_user(db, user_in)
        return web.json_response(
            {
                "key": db_user["key"],
                "username": db_user["username"],
                "name": db_user["name"],
                "email": db_user["email"],
                "is_active": db_user["is_active"],
                "created_at": db_user["created_at"].isoformat(),
                "success": True,
            }
        )
    except Exception as e:
        if isinstance(e, web.HTTPException):
            raise e
        raise web.HTTPInternalServerError(
            text=f"Internal server error while creating user (original error message: {e})",
        )


@routes.put(
    "/api/v1/users/{key}",
)
async def update_user(
    request: web.Request,
    key: str,
):
    db = request["conn"]
    user_in = await request.json()
    try:
        # Check if the user is the current user
        current_user = await AuthService.get_user(db, request["user"])
        if current_user.key != key:
            raise web.HTTPForbidden(text="You are not allowed to update this user")
        user = await UserService.update_user(db, key, user_in)
        return web.json_response(
            {
                "key": user["key"],
                "username": user["username"],
                "name": user["name"],
                "email": user["email"],
                "is_active": user["is_active"],
                "created_at": user["created_at"].isoformat(),
                "success": True,
            }
        )
    except Exception as e:
        if isinstance(e, web.HTTPException):
            raise e
        raise web.HTTPInternalServerError(
            text=f"Internal server error while updating user (original error message: {e})",
        )


@routes.put(
    "/api/v1/users/{key}/password",
)
async def update_user_password(
    request: web.Request,
    key: str,
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
        if current_user.key != user_key:
            raise web.HTTPForbidden(text="You are not allowed to update this user")
        # Update the user password
        user_in = await request.json()
        await UserService.update_user_password(db, user_key, user_in)
        return web.json_response(
            {
                "message": "User password updated successfully",
                "success": True,
            }
        )
    except Exception as e:
        if isinstance(e, web.HTTPException):
            raise e
        raise web.HTTPInternalServerError(
            text=f"Internal server error while updating user password (original error message: {e})",
        )


@routes.delete(
    "/api/v1/users/{key}",
)
async def delete_user(
    request: web.Request,
    key: str,
):
    db = request["conn"]
    try:
        # Check if the user is the current user
        current_user = await AuthService.get_user(db, request["user"])
        if current_user.key != key:
            raise web.HTTPForbidden(text="You are not allowed to delete this user")
        # Delete the user
        user = await UserService.get_user_by_key(db, key)
        if not user:
            raise web.HTTPNotFound(text=f"User with key {key} not found")
        await UserService.delete_user(db, key)
        return web.json_response(
            {
                "message": "User deleted successfully",
                "success": True,
            }
        )
    except Exception as e:
        if isinstance(e, web.HTTPException):
            raise e
        raise web.HTTPInternalServerError(
            text=f"Internal server error while deleting user (original error message: {e})",
        )
