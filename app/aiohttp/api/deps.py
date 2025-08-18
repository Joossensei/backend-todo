import functools
from typing import Iterable, Optional, Set, Dict, Any

from aiohttp import web
from app.core.security import TokenManager
import jwt


def _bearer_unauthorized(error: str, desc: str) -> web.Response:
    # RFC 6750 WWW-Authenticate header
    hdr = f'Bearer realm="api", error="{error}", error_description="{desc}"'
    return web.json_response(
        {"detail": desc}, headers={"WWW-Authenticate": hdr}, status=401
    )


def _forbidden(desc: str) -> web.Response:
    return web.json_response({"detail": desc}, status=403)


def _extract_bearer(request: web.Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return auth[7:].strip() or None


def _decode_jwt(token: str) -> Dict[str, Any]:
    return TokenManager.decode(token)


def _scopes_from_claims(claims: Dict[str, Any]) -> Set[str]:
    # Veel providers gebruiken "scope" (spatie-gescheiden) of "scp" (lijst)
    if "scope" in claims and isinstance(claims["scope"], str):
        return set(claims["scope"].split())
    if "scp" in claims and isinstance(claims["scp"], (list, tuple)):
        return set(claims["scp"])
    return set()


# ---- Middleware: parse & verify (niet handhaven) ----
@web.middleware
async def auth_parsing_middleware(request: web.Request, handler):
    print("auth_parsing_middleware", request)
    token = _extract_bearer(request)
    if token is None:
        # Publieke request; geen user
        request["user"] = None
        request["claims"] = None
        return await handler(request)

    try:
        claims = _decode_jwt(token)
    except jwt.ExpiredSignatureError:
        return _bearer_unauthorized("invalid_token", "Token expired")
    except jwt.InvalidTokenError as e:
        return _bearer_unauthorized("invalid_token", str(e) or "Invalid token")

    # Sla claims op voor downstream handlers/decorators
    request["claims"] = claims
    request["user"] = claims.get(
        "sub"
    )  # of 'preferred_username', afhankelijk van je IdP
    return await handler(request)


# ---- Decorator: handhaaf auth/scopes op specifieke routes ----
def require_auth(scopes: Optional[Iterable[str]] = None, any_scope: bool = False):
    needed = set(scopes or [])

    def decorator(handler):
        @functools.wraps(handler)
        async def wrapped(request: web.Request, *args, **kwargs):
            claims = request.get("claims")
            if not claims:
                print("no claims")
                return _bearer_unauthorized("invalid_token", "Missing or invalid token")

            if needed:
                have = _scopes_from_claims(claims)
                ok = bool(have & needed) if any_scope else needed.issubset(have)
                if not ok:
                    print("insufficient scope")
                    return _forbidden("Insufficient scope")

            return await handler(request, *args, **kwargs)

        return wrapped

    return decorator
