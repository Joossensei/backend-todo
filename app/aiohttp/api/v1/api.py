from aiohttp import web


# ---------- Error -> JSON ----------
@web.middleware
async def error_middleware(request: web.Request, handler):
    try:
        return await handler(request)
    except web.HTTPException as ex:
        if ex.content_type is None:
            return web.json_response({"detail": ex.text or ex.reason}, status=ex.status)
        raise
    except Exception as e:
        return web.json_response({"detail": f"Internal Server Error: {e}"}, status=500)


# ---------- DB-middleware (per request one connection) ----------
@web.middleware
async def db_connection_middleware(request: web.Request, handler):
    pool = request.app["db_pool"]
    async with pool.acquire() as conn:
        request["conn"] = conn
        return await handler(request)
