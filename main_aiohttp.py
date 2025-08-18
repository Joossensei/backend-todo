import logging
from aiohttp import web
from db.conn import init_db, close_db
from app.middleware.config import get_middleware_stack
from app.api.v1.route_manager import register_all_routes

logging.basicConfig(level=logging.DEBUG)


def create_app() -> web.Application:
    app = web.Application(middlewares=get_middleware_stack())
    app.add_routes(register_all_routes())
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
