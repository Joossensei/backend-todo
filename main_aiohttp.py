import logging
from aiohttp import web
from db.conn import init_db, close_db
from app.aiohttp.api.v1.endpoints import token
from app.aiohttp.api.v1 import api
from app.aiohttp.api.deps import auth_parsing_middleware, require_auth
from app.aiohttp.api.v1.cors import make_cors_middleware
from app.aiohttp.api.v1.endpoints import priorities
from app.aiohttp.api.v1.endpoints import todos
from app.aiohttp.api.v1.endpoints import user

routes = web.RouteTableDef()


@routes.get("/")
async def root(request):
    return web.json_response({"message": "Welcome to Todo API", "version": "0.1.0"})


@routes.get("/health")
@require_auth()
async def health(request):
    return web.json_response({"status": "ok"})


@routes.post("/api/v1/token")
@require_auth()
async def token_route(request):
    return await token.login_for_access_token(request)


# Todos
@routes.get("/api/v1/todos")
@require_auth()
async def get_todos(request):
    return await todos.get_todos(request)


@routes.get("/api/v1/todo/{key}")
@require_auth()
async def get_todo_by_key(request):
    return await todos.get_todo_by_key(request)


@routes.put("/api/v1/todo/{key}")
@require_auth()
async def update_todo(request):
    return await todos.update_todo(request)


@routes.post("/api/v1/todos")
@require_auth()
async def create_todo(request):
    return await todos.create_todo(request)


@routes.patch("/api/v1/todo/{key}")
@require_auth()
async def patch_todo(request):
    return await todos.patch_todo(request)


@routes.delete("/api/v1/todo/{key}")
@require_auth()
async def delete_todo(request):
    return await todos.delete_todo(request)


# Priorities
@routes.get("/api/v1/priorities")
@require_auth()
async def get_priorities(request):
    return await priorities.get_priorities(request)


@routes.get("/api/v1/priority/{key}")
@require_auth()
async def get_priority_by_key(request):
    return await priorities.get_priority_by_key(request)


@routes.post("/api/v1/priorities")
@require_auth()
async def create_priority(request):
    return await priorities.create_priority(request)


@routes.put("/api/v1/priority/{key}")
@require_auth()
async def update_priority(request):
    return await priorities.update_priority(request)


@routes.patch("/api/v1/priority/{key}")
@require_auth()
async def patch_priority(request):
    return await priorities.patch_priority(request)


@routes.delete("/api/v1/priority/{key}")
@require_auth()
async def delete_priority(request):
    return await priorities.delete_priority(request)


# Users


@routes.get("/api/v1/users")
@require_auth()
async def get_users(request):
    return await user.get_users(request)


@routes.get("/api/v1/user/{key}")
@require_auth()
async def get_user_by_key(request):
    return await user.get_user_by_key(request)


@routes.post("/api/v1/users")
@require_auth()
async def create_user(request):
    return await user.create_user(request)


@routes.put("/api/v1/user/{key}")
@require_auth()
async def update_user(request):
    return await user.update_user(request)


@routes.put("/api/v1/user/{key}/password")
@require_auth()
async def update_user_password(request):
    return await user.update_user_password(request)


@routes.delete("/api/v1/user/{key}")
@require_auth()
async def delete_user(request):
    return await user.delete_user(request)


logging.basicConfig(level=logging.DEBUG)


def create_app() -> web.Application:
    cors = make_cors_middleware(
        allowed_origins={
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        },
        allow_credentials=False,  # zet op True als je cookies/auth via browser gebruikt
        strict_block=True,  # block elke onbekende Origin met 403
        exposed_headers=["X-Request-Id"],  # optioneel
    )
    app = web.Application(
        middlewares=[
            cors,
            api.error_middleware,
            api.db_connection_middleware,
            auth_parsing_middleware,
        ],
    )
    app.add_routes(routes)
    app.on_startup.append(init_db)
    app.on_cleanup.append(close_db)
    return app


if __name__ == "__main__":
    web.run_app(
        create_app(),
        host="localhost",
        port=8000,
        access_log_format='\n%a | %t \n"%r" \nStatus: %s | Resp Size: %b | Time: %T'
        "\n-------------------------------------------------",
    )
