"""
Routes package for API v1.

This package contains route definitions organized by resource type.
Each resource has its own route module for better organization.
"""

from .base import apply_base_routes
from .todos import apply_todo_routes
from .priorities import apply_priority_routes
from .users import apply_user_routes
from .auth import apply_auth_routes
from .statuses import apply_status_routes

__all__ = [
    "apply_base_routes",
    "apply_todo_routes",
    "apply_priority_routes",
    "apply_user_routes",
    "apply_auth_routes",
    "apply_status_routes",
]
