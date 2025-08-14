from aiohttp import web
from aiohttp_cors import setup as cors_setup, ResourceOptions
from app.api.v1.api import setup_routes
from datetime import datetime
from app import __version__
from app.core.rate_limit import RateLimiter
from app.database import close_pool


async def root_handler(request):
    """Root endpoint handler."""
    return web.json_response(
        {
            "message": "Welcome to Todo API",
            "version": __version__,
            "docs": "/docs",
        }
    )


async def health_handler(request):
    """Health check endpoint handler."""
    return web.json_response(
        {"status": "healthy", "timestamp": datetime.now().isoformat()}
    )


def create_app():
    """Create and configure the AIOHTTP application."""
    app = web.Application()

    # Setup CORS
    cors = cors_setup(
        app,
        defaults={
            "*": ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*",
            )
        },
    )

    # Setup rate limiter
    rate_limiter = RateLimiter()
    app["rate_limiter"] = rate_limiter

    # Add middleware for rate limiting
    app.middlewares.append(rate_limiter.middleware)

    # Setup routes
    app.router.add_get("/", root_handler)
    app.router.add_get("/health", health_handler)

    # Setup API routes
    setup_routes(app, cors)

    # Setup cleanup on shutdown
    async def cleanup(app):
        await close_pool()

    app.on_cleanup.append(cleanup)

    return app

app = create_app()


if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000)
