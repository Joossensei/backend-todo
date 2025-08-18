"""
Logging middleware for AioHTTP application.

This module contains middleware functions for request/response logging.
"""

import logging
import time
from aiohttp import web
import uuid

REQUEST_ID_HEADER = "X-Request-Id"

logger = logging.getLogger(__name__)


def get_request_id(request: web.Request) -> str:
    return request.get("request_id", "")


@web.middleware
async def request_logging_middleware(request: web.Request, handler):
    """
    Request logging middleware.

    Logs incoming requests and their responses with timing information.
    Useful for monitoring and debugging.
    """
    start_time = time.time()

    # Log incoming request
    logger.info(
        f"Request started: {request.method} {request.path} from {request.remote}"
    )

    request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid.uuid4()))
    request["request_id"] = request_id

    try:
        response = await handler(request)
        response.headers.setdefault(REQUEST_ID_HEADER, request_id)

        # Log successful response
        duration = time.time() - start_time
        logger.info(
            f"Request completed: {request.method} {request.path} "
            f"- Status: {response.status} - Duration: {duration:.3f}s"
        )

        return response

    except Exception as e:
        # Log failed request
        duration = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.path} "
            f"- Error: {str(e)} - Duration: {duration:.3f}s"
        )
        raise
