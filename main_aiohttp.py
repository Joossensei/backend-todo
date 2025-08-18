import logging
from aiohttp import web
from db.conn import init_db, close_db
from app.api.v1 import api
from app.middleware.config import get_middleware_stack

routes = web.RouteTableDef()

routes = api.apply_endpoints(routes)

logging.basicConfig(level=logging.DEBUG)


def create_app() -> web.Application:
    app = web.Application(middlewares=get_middleware_stack())
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
