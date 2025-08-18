# app/api/v1/endpoints/todos.py
from aiohttp import web
from app.services.priority_service import PriorityService
from app.services.auth_service import AuthService
from app.utils.mapping import record_to_dict
from app.schemas.priority import PriorityResponse, PriorityListResponse
from app.utils.pagination import build_pagination_link
from app.core.errors import AppError, NotFoundError
import logging

logger = logging.getLogger(__name__)


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
        items = [PriorityResponse(**record_to_dict(p)) for p in priorities]
        return web.json_response(
            PriorityListResponse(
                priorities=items,
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
            PriorityResponse(**record_to_dict(priority)).model_dump(),
            status=200,
        )
    except ValueError:
        raise NotFoundError(ValueError(f"Priority with key {key} not found"))
    except Exception as e:
        raise AppError(e)


async def create_priority(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    priority = await request.json()
    try:
        priority = await PriorityService.create_priority(
            db, priority, current_user["key"]
        )
        return web.json_response(
            PriorityResponse(**record_to_dict(priority)).model_dump(),
            status=201,
        )
    except ValueError as e:
        raise AppError(e)
    except Exception as e:
        raise AppError(e)


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
        raise NotFoundError(ValueError(f"Priority with key {key} not found"))
    except Exception as e:
        raise AppError(e)
    try:
        priority = await PriorityService.update_priority(
            db, priority_id, priority, current_user["key"]
        )
        return web.json_response(
            PriorityResponse(**record_to_dict(priority)).model_dump(),
            status=200,
        )
    except Exception as e:
        raise AppError(e)


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
        raise NotFoundError(ValueError(f"Priority with key {key} not found"))
    except Exception as e:
        raise AppError(e)
    try:
        # Only update fields that are provided
        updated_priority = await PriorityService.patch_priority(
            db, priority_id, priority_patch, current_user["key"]
        )
        return web.json_response(
            PriorityResponse(**record_to_dict(updated_priority)).model_dump(),
            status=200,
        )
    except Exception as e:
        raise AppError(e)


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
            return web.Response(status=204)
        else:
            raise AppError(ValueError("Failed to delete priority"))
    except ValueError:
        raise NotFoundError(ValueError(f"Priority with key {key} not found"))
    except Exception as e:
        raise AppError(e)
