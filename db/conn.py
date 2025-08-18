from aiohttp import web
import asyncpg
from app.core.config import settings

# ---------- App factory + lifecycle ----------


async def init_db(app: web.Application):
    dsn = settings.database_url
    app["db_pool"] = await asyncpg.create_pool(
        dsn=dsn,
        min_size=settings.db_pool_min,
        max_size=settings.db_pool_max,
        command_timeout=60,
    )


async def close_db(app: web.Application):
    await app["db_pool"].close()
