import asyncpg
from app.schemas.user import UserCreate
from app.core.security import TokenManager
import uuid
from typing import Optional, Dict, Any


class UserService:
    @staticmethod
    async def create_user(
        connection: asyncpg.Connection, user: UserCreate
    ) -> Dict[str, Any]:
        """Create a new user."""
        # Check if username already exists
        existing_user = await connection.fetchrow(
            "SELECT id FROM users WHERE username = $1", user.username
        )
        if existing_user:
            raise ValueError("Username already exists")

        # Hash password
        hashed_password = TokenManager.hash_password(user.password)

        # Create user
        user_key = str(uuid.uuid4())
        user_data = await connection.fetchrow(
            """
            INSERT INTO users (key, name, username, email, hashed_password, is_active)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, key, name, username, email, hashed_password, is_active, created_at, updated_at
        """,
            user_key,
            user.name,
            user.username,
            user.email,
            hashed_password,
            user.is_active,
        )

        return dict(user_data)

    @staticmethod
    async def get_user_by_username(
        connection: asyncpg.Connection, username: str
    ) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        user_data = await connection.fetchrow(
            "SELECT * FROM users WHERE username = $1", username
        )

        if not user_data:
            return None

        return dict(user_data)

    @staticmethod
    async def get_user_by_key(
        connection: asyncpg.Connection, key: str
    ) -> Optional[Dict[str, Any]]:
        """Get user by key."""
        user_data = await connection.fetchrow("SELECT * FROM users WHERE key = $1", key)

        if not user_data:
            return None

        return dict(user_data)
