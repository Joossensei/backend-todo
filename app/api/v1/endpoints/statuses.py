# app/api/v1/endpoints/statuses.py
from aiohttp import web
from app.services.status_service import StatusService
from app.services.auth_service import AuthService
from app.utils.mapping import record_to_dict
from app.schemas.status import (
    StatusResponse,
    StatusListResponse,
    StatusCreate,
    StatusPatch,
    StatusUpdate,
    StatusReorder,
)
from app.utils.pagination import build_pagination_link, parse_pagination
from app.core.errors import AppError, NotFoundError, UnauthorizedError, ValidationError
import logging
from app.middleware.authentication import require_auth
from app.validators.status_validator import (
    StatusCreateValidator,
    StatusUpdateValidator,
    StatusPatchValidator,
)
import pydantic

logger = logging.getLogger(__name__)


@require_auth()
async def get_statuses(request: web.Request):
    db = request["conn"]
    username = request["user"]
    if not username:
        raise UnauthorizedError(ValueError("Unauthorized"))
    current_user = await AuthService.get_user(db, username)
    page, size, skip = parse_pagination(
        request.query.get("page"), request.query.get("size")
    )
    try:
        statuses = await StatusService.get_statuses(db, current_user["key"], skip, size)
        if not statuses:
            return web.json_response(
                StatusListResponse(
                    statuses=[],
                    total=0,
                    page=page,
                    size=0,
                    success=True,
                    next_link=None,
                    prev_link=None,
                ).model_dump(),
                status=200,
            )
        total = await StatusService.get_total_statuses(db, current_user["key"])
        items = [StatusResponse(**record_to_dict(p)) for p in statuses]
        return web.json_response(
            StatusListResponse(
                statuses=items,
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
        logger.error(f"Error getting statuses: {e}")
        raise AppError(e)


@require_auth()
async def get_status_by_key(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    try:
        status_id = await StatusService.fetch_status_id_by_key(
            db, key, current_user["key"]
        )
        if not status_id:
            raise NotFoundError(f"Status with key {key} not found")
        status = await StatusService.get_status(db, status_id, current_user["key"])
        return web.json_response(
            StatusResponse(**record_to_dict(status)).model_dump(),
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
        logger.error(f"Error getting status by key: {e}")
        raise AppError(e)


@require_auth()
async def create_status(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    status_data = await request.json()
    try:
        # Check if all fields are present
        if not all(
            key in status_data for key in ["name", "color", "icon", "order", "user_key"]
        ):
            raise ValidationError(custom_message="All fields are required")
        status_model = StatusCreate(**status_data)
        status_model = StatusCreateValidator.validate_status(status_model)
        status = await StatusService.create_status(
            db, status_model, current_user["key"]
        )
        return web.json_response(
            StatusResponse(**record_to_dict(status)).model_dump(),
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
        logger.error(f"Error creating status: {e}")
        raise AppError(e)


@require_auth()
async def update_status(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    status_data = await request.json()
    try:
        status_id = await StatusService.fetch_status_id_by_key(
            db, key, current_user["key"]
        )
    except NotFoundError:
        raise
    except Exception as e:
        raise AppError(e)
    try:
        status_model = StatusUpdate(**status_data)
        status_model = StatusUpdateValidator.validate_status(status_model)
        status = await StatusService.update_status(
            db, status_id, status_model, current_user["key"]
        )
        return web.json_response(
            StatusResponse(**record_to_dict(status)).model_dump(),
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
        logger.error(f"Error updating status: {e}")
        raise AppError(e)


@require_auth()
async def patch_status(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    status_patch = await request.json()
    try:
        status_id = await StatusService.fetch_status_id_by_key(
            db, key, current_user["key"]
        )
    except NotFoundError:
        raise
    except Exception as e:
        raise AppError(e)

    try:
        status_model = StatusPatch(**status_patch)
        status_model = StatusPatchValidator.validate_status(status_model)
        updated_status = await StatusService.patch_status(
            db, status_id, status_model, current_user["key"]
        )
        return web.json_response(
            StatusResponse(**record_to_dict(updated_status)).model_dump(),
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
        logger.error(f"Error patching status: {e}")
        raise AppError(e)


@require_auth()
async def delete_status(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    try:
        status_id = await StatusService.fetch_status_id_by_key(
            db, key, current_user["key"]
        )
        await StatusService.delete_status(db, status_id, current_user["key"])
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
        logger.error(f"Error deleting status: {e}")
        raise AppError(e)


@require_auth()
async def reorder_statuses(request: web.Request):
    """Reorder statuses by moving from one order position to another."""
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    reorder_data = await request.json()

    try:
        # Validate the request body
        reorder_model = StatusReorder(**reorder_data)

        # Perform the reordering
        updated_statuses = await StatusService.reorder_statuses(
            db, reorder_model, current_user["key"]
        )

        # Convert to response format
        items = [StatusResponse(**record_to_dict(p)) for p in updated_statuses]

        return web.json_response(
            StatusListResponse(
                statuses=items,
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
        logger.error(f"Error reordering statuses: {e}")
        raise AppError(e)
