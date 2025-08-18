# app/api/v1/endpoints/todos.py
from aiohttp import web
from db.services.priority_service import PriorityService
from db.services.auth_service import AuthService


async def get_priorities(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    page = request.query.get("page", 1)
    size = request.query.get("size", 10)
    try:
        skip = (page - 1) * size
        priorities = await PriorityService.get_priorities(
            db, current_user["key"], skip, size
        )
        total = await PriorityService.get_total_priorities(db, current_user["key"])
        resp = []
        for priority in priorities:
            resp.append(
                {
                    "key": priority["key"],
                    "name": priority["name"],
                    "description": priority["description"],
                    "color": priority["color"],
                    "icon": priority["icon"],
                    "order": priority["order"],
                    "user_key": priority["user_key"],
                    "created_at": priority["created_at"].isoformat(),
                    "updated_at": (
                        priority["updated_at"].isoformat()
                        if priority["updated_at"]
                        else None
                    ),
                }
            )
        return web.json_response(
            {
                "priorities": resp,
                "total": total,
                "page": page,
                "size": size,
                "success": True,
                "next_link": (
                    f"/api/v1/priorities?page={page + 1}&size={size}"
                    if page * size < total
                    else None
                ),
                "prev_link": (
                    f"/api/v1/priorities?page={page - 1}&size={size}"
                    if page > 1
                    else None
                ),
            }
        )
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while getting priorities (original error message: {e})",
        )


async def get_priority_by_key(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    try:
        priority_id = await PriorityService.fetch_priority_id_by_key(
            db, key, current_user["key"]
        )
        priority = await PriorityService.get_priority(
            db, priority_id, current_user["key"]
        )
        return web.json_response(
            {
                "key": priority["key"],
                "name": priority["name"],
                "description": priority["description"],
                "color": priority["color"],
                "icon": priority["icon"],
                "order": priority["order"],
                "user_key": priority["user_key"],
                "created_at": priority["created_at"].isoformat(),
                "updated_at": (
                    priority["updated_at"].isoformat()
                    if priority["updated_at"]
                    else None
                ),
                "success": True,
            }
        )
    except ValueError:
        raise web.HTTPNotFound(text=f"Priority with key {key} not found")
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while getting priority by key (original error message: {e})",
        )


async def create_priority(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    priority = await request.json()
    try:
        priority = await PriorityService.create_priority(
            db, priority, current_user["key"]
        )
        print(priority)
        return web.json_response(
            {
                "key": priority["key"],
                "name": priority["name"],
                "description": priority["description"],
                "color": priority["color"],
                "icon": priority["icon"],
                "order": priority["order"],
                "user_key": priority["user_key"],
                "created_at": priority["created_at"].isoformat(),
                "success": True,
            }
        )
    except ValueError as e:
        raise web.HTTPBadRequest(text=str(e))
    except Exception as e:
        print(e.with_traceback(e.__traceback__))
        raise web.HTTPInternalServerError(
            text=f"Internal server error while creating priority (original error message: {e.with_traceback(e.__traceback__)})",
        )


async def update_priority(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    priority = await request.json()
    try:
        priority_id = await PriorityService.fetch_priority_id_by_key(
            db, key, current_user["key"]
        )
    except ValueError:
        raise web.HTTPNotFound(text=f"Priority with key {key} not found")
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while updating priority (original error message: {e})",
        )
    try:
        priority = await PriorityService.update_priority(
            db, priority_id, priority, current_user["key"]
        )
        return web.json_response(
            {
                "key": priority["key"],
                "name": priority["name"],
                "description": priority["description"],
                "color": priority["color"],
                "icon": priority["icon"],
                "order": priority["order"],
                "user_key": priority["user_key"],
                "created_at": priority["created_at"].isoformat(),
                "updated_at": (
                    priority["updated_at"].isoformat()
                    if priority["updated_at"]
                    else None
                ),
                "success": True,
            }
        )
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while updating priority (original error message: {e})",
        )


async def patch_priority(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    priority_patch = await request.json()
    try:
        priority_id = await PriorityService.fetch_priority_id_by_key(
            db, key, current_user["key"]
        )
    except ValueError:
        raise web.HTTPNotFound(text=f"Priority with key {key} not found")
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while patching priority (original error message: {e})",
        )
    try:
        # Only update fields that are provided
        updated_priority = await PriorityService.patch_priority(
            db, priority_id, priority_patch, current_user["key"]
        )
        return web.json_response(
            {
                "key": updated_priority["key"],
                "name": updated_priority["name"],
                "description": updated_priority["description"],
                "color": updated_priority["color"],
                "icon": updated_priority["icon"],
                "order": updated_priority["order"],
                "user_key": updated_priority["user_key"],
                "created_at": updated_priority["created_at"].isoformat(),
                "updated_at": updated_priority["updated_at"].isoformat(),
                "success": True,
            }
        )
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while updating priority (original error message: {e})",
        )


async def delete_priority(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    try:
        priority_id = await PriorityService.fetch_priority_id_by_key(
            db, key, current_user["key"]
        )
        if await PriorityService.delete_priority(db, priority_id, current_user["key"]):
            return web.json_response(
                {"message": "Priority deleted successfully", "success": True}
            )
        else:
            raise web.HTTPInternalServerError(
                text="Internal server error while deleting priority"
            )
    except ValueError:
        raise web.HTTPNotFound(text=f"Priority with key {key} not found")
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while deleting priority (original error message: {e})",
        )
