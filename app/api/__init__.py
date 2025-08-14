"""API package exports."""

# Expose authentication helpers for easy import while avoiding heavy imports
# in modules that don't need them.
from .deps import get_current_user_middleware, get_current_active_user

__all__ = [
    "get_current_user_middleware",
    "get_current_active_user",
]
