"""
Error handling middleware for AioHTTP application.

This module contains middleware functions for handling exceptions and errors
that occur during request processing.
"""

import logging
from aiohttp import web
from app.core.errors import AppError
from app.middleware.logging import get_request_id  # helper below
from app.middleware.cors import _apply_cors

logger = logging.getLogger(__name__)


@web.middleware
async def error_middleware(request: web.Request, handler):
    """
    Global error handling middleware.

    Catches all exceptions and converts them to appropriate HTTP responses.
    Logs errors for debugging and monitoring.
    """
    try:
        return await handler(request)
    except AppError as ex:
        logger.error(f"AppError: {ex.message}")
        resp = ex.to_response(get_request_id(request))
        _apply_cors(request, resp)
        return resp
    except web.HTTPException as ex:
        logger.error(f"HTTPException: {ex.text or ex.reason}")
        resp = web.json_response(
            {
                "error": {"code": "http_error", "message": ex.text or ex.reason},
                "request_id": get_request_id(request),
            },
            status=ex.status,
        )
        _apply_cors(request, resp)
        return resp
    except Exception as e:
        logger.error(f"Unhandled server error: {e}")
        resp = web.json_response(
            {
                "error": {"code": "internal_error", "message": "Internal Server Error"},
                "request_id": get_request_id(request),
            },
            status=500,
        )
        _apply_cors(request, resp)
        return resp
