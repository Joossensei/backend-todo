import logging
from aiohttp import web
from app.aiohttp.api.v1.cors import _apply_cors

logger = logging.getLogger(__name__)


# ---------- Error -> JSON ----------
@web.middleware
async def error_middleware(request: web.Request, handler):
    try:
        return await handler(request)
    except web.HTTPException as ex:
        logger.error(f"HTTPException: {ex.text or ex.reason}")
        if ex.content_type is None:
            resp = web.json_response(
                {"detail": ex.text or ex.reason},
                status=ex.status,
            )
            _apply_cors(request, resp)
            return resp
        else:
            resp = web.Response(
                text=ex.text or ex.reason,
                status=ex.status,
                content_type=ex.content_type,
            )
            _apply_cors(request, resp)
            return resp
    except Exception as e:
        logger.error(f"Exception: {e}")
        resp = web.json_response({"detail": f"Internal Server Error: {e}"}, status=500)
        _apply_cors(request, resp)
        return resp


# ---------- DB-middleware (per request one connection) ----------
@web.middleware
async def db_connection_middleware(request: web.Request, handler):
    pool = request.app["db_pool"]
    async with pool.acquire() as conn:
        request["conn"] = conn
        return await handler(request)
