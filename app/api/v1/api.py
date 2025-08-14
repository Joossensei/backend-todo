# app/api/v1/api.py
from aiohttp import web
from app.api.v1.endpoints import todos, priorities, token, user
from app.api import get_current_user_middleware


def setup_routes(app: web.Application, cors):
    """Setup all API routes for AIOHTTP."""

    # Add authentication middleware
    app.middlewares.append(get_current_user_middleware)

    # Setup todos routes
    todos.setup_routes(app, cors, "/api/v1/todos")

    # Setup priorities routes
    priorities.setup_routes(app, cors, "/api/v1/priorities")

    # Setup token routes
    token.setup_routes(app, cors, "/api/v1")

    # Setup user routes
    user.setup_routes(app, cors, "/api/v1/users")
