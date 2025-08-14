from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request


def user_or_ip_key(request: Request) -> str:
    """Use per-user key when authenticated, else fall back to client IP."""
    user = getattr(request.state, "user", None)
    if user is not None and getattr(user, "key", None):
        return f"user:{user.key}"
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(
    key_func=user_or_ip_key,
    headers_enabled=True,
)
