# app/services/priority_service.py
import asyncpg
from typing import Optional, List, Dict, Any


class PriorityService:
    @staticmethod
    async def get_priorities(
        connection: asyncpg.Connection, user_key: str, skip: int = 0, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get priorities for a user with pagination."""
        priorities_data = await connection.fetch(
            """
            SELECT id, key, name, order_num, user_key, created_at, updated_at
            FROM priorities 
            WHERE user_key = $1
            ORDER BY order_num ASC
            LIMIT $2 OFFSET $3
        """,
            user_key,
            limit,
            skip,
        )

        return [dict(priority) for priority in priorities_data]

    @staticmethod
    async def get_total_priorities(
        connection: asyncpg.Connection, user_key: str
    ) -> int:
        """Get total count of priorities for a user."""
        result = await connection.fetchval(
            "SELECT COUNT(*) FROM priorities WHERE user_key = $1", user_key
        )
        return result

    @staticmethod
    async def get_priority_by_key(
        connection: asyncpg.Connection, key: str, user_key: str
    ) -> Optional[Dict[str, Any]]:
        """Get a priority by its UUID key."""
        priority_data = await connection.fetchrow(
            """
            SELECT id, key, name, order_num, user_key, created_at, updated_at
            FROM priorities 
            WHERE key = $1 AND user_key = $2
        """,
            key,
            user_key,
        )

        if not priority_data:
            return None

        return dict(priority_data)
