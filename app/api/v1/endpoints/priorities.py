# app/api/v1/endpoints/todos.py
from aiohttp import web
from app.services.priority_service import PriorityService
from app.services.auth_service import AuthService
from app.utils.mapping import record_to_dict
from app.schemas.priority import (
    PriorityResponse,
    PriorityListResponse,
    PriorityCreate,
    PriorityPatch,
    PriorityUpdate,
    PriorityReorder,
)
from app.utils.pagination import build_pagination_link, parse_pagination
from app.core.errors import AppError, NotFoundError, UnauthorizedError, ValidationError
import logging
from app.middleware.authentication import require_auth
from app.validators.priority_validator import (
    PriorityCreateValidator,
    PriorityUpdateValidator,
    PriorityPatchValidator,
)
import pydantic

logger = logging.getLogger(__name__)


@require_auth()
async def get_priorities(request: web.Request):
    db = request["conn"]
    username = request["user"]
    if not username:
        raise UnauthorizedError(ValueError("Unauthorized"))
    current_user = await AuthService.get_user(db, username)
    page, size, skip = parse_pagination(
        request.query.get("page"), request.query.get("size")
    )
    try:
        priorities = await PriorityService.get_priorities(
            db, current_user["key"], skip, size
        )
        if not priorities:
            return web.json_response(
                PriorityListResponse(
                    priorities=[],
                    total=0,
                    page=page,
                    size=0,
                    success=True,
                    next_link=None,
                    prev_link=None,
                ).model_dump(),
                status=200,
            )
        total = await PriorityService.get_total_priorities(db, current_user["key"])
        items = [PriorityResponse(**record_to_dict(p)) for p in priorities]
        return web.json_response(
            PriorityListResponse(
                priorities=items,
                total=total,
                page=page,
                size=len(items),
                success=True,
                next_link=build_pagination_link(request.url, page + 1, size, total),
                prev_link=build_pagination_link(request.url, page - 1, size, total),
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
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error getting priorities: {e}")
        raise AppError(e)


@require_auth()
async def get_priority_by_key(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    try:
        priority_id = await PriorityService.fetch_priority_id_by_key(
            db, key, current_user["key"]
        )
        if not priority_id:
            raise NotFoundError(f"Priority with key {key} not found")
        priority = await PriorityService.get_priority(
            db, priority_id, current_user["key"]
        )
        return web.json_response(
            PriorityResponse(**record_to_dict(priority)).model_dump(),
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
        logger.error(f"Error getting priority by key: {e}")
        raise AppError(e)


@require_auth()
async def create_priority(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    priority_data = await request.json()
    try:
        # Check if all fields are present
        if not all(
            key in priority_data
            for key in ["name", "color", "icon", "order", "user_key"]
        ):
            raise ValidationError(custom_message="All fields are required")
        priority_model = PriorityCreate(**priority_data)
        priority_model = PriorityCreateValidator.validate_priority(
            priority_model, current_user["key"]
        )
        priority = await PriorityService.create_priority(
            db, priority_model, current_user["key"]
        )
        return web.json_response(
            PriorityResponse(**record_to_dict(priority)).model_dump(),
            status=201,
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
        logger.error(f"Error creating priority: {e}")
        raise AppError(e)


@require_auth()
async def update_priority(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    priority_data = await request.json()
    try:
        priority_id = await PriorityService.fetch_priority_id_by_key(
            db, key, current_user["key"]
        )
    except NotFoundError:
        raise
    except Exception as e:
        raise AppError(e)
    try:
        priority_model = PriorityUpdate(**priority_data)
        priority_model = PriorityUpdateValidator.validate_priority(priority_model)
        priority = await PriorityService.update_priority(
            db, priority_id, priority_model, current_user["key"]
        )
        return web.json_response(
            PriorityResponse(**record_to_dict(priority)).model_dump(),
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
        logger.error(f"Error updating priority: {e}")
        raise AppError(e)


@require_auth()
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
    except NotFoundError:
        raise
    except Exception as e:
        raise AppError(e)

    try:
        priority_model = PriorityPatch(**priority_patch)
        priority_model = PriorityPatchValidator.validate_priority(priority_model)
        updated_priority = await PriorityService.patch_priority(
            db, priority_id, priority_model, current_user["key"]
        )
        return web.json_response(
            PriorityResponse(**record_to_dict(updated_priority)).model_dump(),
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
        logger.error(f"Error patching priority: {e}")
        raise AppError(e)


@require_auth()
async def delete_priority(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    try:
        priority_id = await PriorityService.fetch_priority_id_by_key(
            db, key, current_user["key"]
        )
        await PriorityService.delete_priority(db, priority_id, current_user["key"])
        return web.Response(status=204)
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
        logger.error(f"Error deleting priority: {e}")
        raise AppError(e)


@require_auth()
async def reorder_priorities(request: web.Request):
    """Reorder priorities by moving from one order position to another."""
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    reorder_data = await request.json()

    try:
        # Validate the request body
        reorder_model = PriorityReorder(**reorder_data)

        # Perform the reordering
        updated_priorities = await PriorityService.reorder_priorities(
            db, reorder_model, current_user["key"]
        )

        # Convert to response format
        items = [PriorityResponse(**record_to_dict(p)) for p in updated_priorities]

        return web.json_response(
            PriorityListResponse(
                priorities=items,
                total=len(items),
                page=1,
                size=len(items),
                success=True,
                next_link=None,
                prev_link=None,
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
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error reordering priorities: {e}")
        raise AppError(e)
