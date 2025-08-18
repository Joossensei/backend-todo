# cors.py
import logging
from typing import Iterable, Set, Optional
from aiohttp import web

logger = logging.getLogger(__name__)

allowed = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}


def make_cors_middleware(
    allowed_origins: Iterable[str],
    allow_credentials: bool = False,
    strict_block: bool = True,  # 403 als Origin aanwezig maar niet toegestaan
    exposed_headers: Optional[Iterable[str]] = None,
):
    allowed: Set[str] = set(allowed_origins)
    exposed = ", ".join(exposed_headers or [])

    @web.middleware
    async def cors_middleware(request: web.Request, handler):
        origin = request.headers.get("Origin")

        # Geen Origin = geen CORS (server-to-server of curl). Laat door.
        if not origin:
            return await handler(request)

        # Origin aanwezig: check whitelist
        if origin not in allowed:
            if strict_block:
                return web.json_response(
                    {"detail": "CORS origin not allowed"}, status=403
                )
            # Niet strict: behandel als non-CORS
            return await handler(request)

        # Preflight (OPTIONS + Access-Control-Request-Method)
        if request.method == "OPTIONS" and request.headers.get(
            "Access-Control-Request-Method"
        ):
            acrm = request.headers.get("Access-Control-Request-Method", "")
            acrh = request.headers.get("Access-Control-Request-Headers", "")
            headers = {
                "Access-Control-Allow-Origin": origin,
                "Vary": "Origin",
                "Access-Control-Allow-Methods": acrm
                or "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": acrh or "Authorization, Content-Type",
                "Access-Control-Max-Age": "600",
            }
            if allow_credentials:
                headers["Access-Control-Allow-Credentials"] = "true"
            if exposed:
                headers["Access-Control-Expose-Headers"] = exposed
            return web.Response(status=204, headers=headers)

        # "Gewone" CORS request: laat door en append headers
        resp = await handler(request)
        # Voeg alleen toe als er nog geen CORS headers zijn gezet
        resp.headers.setdefault("Access-Control-Allow-Origin", origin)
        resp.headers.setdefault("Vary", "Origin")
        if allow_credentials:
            resp.headers.setdefault("Access-Control-Allow-Credentials", "true")
        if exposed:
            resp.headers.setdefault("Access-Control-Expose-Headers", exposed)
        return resp

    return cors_middleware


def _apply_cors(request: web.Request, response: web.StreamResponse) -> None:
    logger.debug(f"Applying CORS to response: {response}")
    origin = request.headers.get("Origin")
    # Kies: strikte whitelist óf wildcard. Met credentials mag je géén '*'.
    if origin in allowed:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"  # belangrijk voor caches
        response.headers["Access-Control-Allow-Credentials"] = "true"
        # Pas aan op je front-end behoeften:
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        )
        response.headers["Access-Control-Expose-Headers"] = (
            "Content-Length, Content-Type"
        )
    else:
        # Of laat weg voor nóg strikter beleid
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = "*"
