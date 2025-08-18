"""
Database middleware for AioHTTP application.

This module contains middleware functions for database connection management.
"""

from aiohttp import web


@web.middleware
async def db_connection_middleware(request: web.Request, handler):
    """
    Database connection middleware.

    Provides a database connection to each request handler.
    Ensures proper connection cleanup after request processing.
    """
    pool = request.app["db_pool"]
    async with pool.acquire() as conn:
        request["conn"] = conn
        return await handler(request)
