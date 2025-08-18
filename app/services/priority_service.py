# app/services/priority_service.py
from app.models.priority import Priority
from app.schemas.priority import PriorityCreate
import uuid
import asyncpg


class PriorityService:
    @staticmethod
    async def create_priority(
        conn: asyncpg.Connection, priority: PriorityCreate, user_key: str
    ) -> Priority:
        async with conn.transaction():
            priority["key"] = str(uuid.uuid4())
            db_priority = await conn.fetchrow(
                """
                INSERT INTO priorities
                        ( "key"
                        , "name"
                        , "description"
                        , "color"
                        , "icon"
                        , "order"
                        , "user_key")
                    VALUES ( $1
                        , $2
                        , $3
                        , $4
                        , $5
                        , $6
                        , $7) RETURNING *
                """,
                priority["key"],
                priority["name"],
                priority["description"],
                priority["color"],
                priority["icon"],
                priority["order"],
                user_key,
            )
            return db_priority

    @staticmethod
    async def fetch_priority_id_by_key(
        conn: asyncpg.Connection, key: str, user_key: str
    ) -> int:
        """Get a priority by its UUID key instead of ID."""
        db_priority = await conn.fetchrow(
            """
            SELECT p.id
            FROM priorities p
            WHERE p.key = $1
            AND p.user_key = $2
            """,
            key,
            user_key,
        )
        return db_priority["id"] if db_priority else None

    @staticmethod
    async def get_priorities(
        conn: asyncpg.Connection, user_key: str, skip: int = 0, limit: int = 10
    ):
        return await conn.fetch(
            """
            SELECT p.*
            FROM priorities p
            WHERE p.user_key = $1
            ORDER BY p.order ASC
            OFFSET $2
            LIMIT $3
            """,
            user_key,
            skip,
            limit,
        )

    @staticmethod
    async def get_priority(conn: asyncpg.Connection, priority_id: int, user_key: str):
        return await conn.fetchrow(
            """
            SELECT p.*
            FROM priorities p
            WHERE p.id = $1
            AND p.user_key = $2
            """,
            priority_id,
            user_key,
        )

    @staticmethod
    async def update_priority(
        conn: asyncpg.Connection,
        priority_id: int,
        priority_update: dict,
        user_key: str,
    ) -> Priority:
        async with conn.transaction():
            # First check if priority exists
            db_priority = await conn.fetchrow(
                """
                SELECT p.*
                FROM priorities p
                WHERE p.id = $1
                AND p.user_key = $2
                """,
                priority_id,
                user_key,
            )
            if not db_priority:
                raise ValueError(f"Priority with id {priority_id} not found")

            # Build dynamic update query
            update_fields = []
            values = []
            param_count = 1

            for field, value in priority_update.items():
                if field in ["name", "description", "color", "icon", "order"]:
                    update_fields.append(f'"{field}" = ${param_count}')
                    values.append(value)
                    param_count += 1

            if not update_fields:
                # No valid fields to update
                return db_priority

            # Add the WHERE clause parameters
            values.extend([priority_id, user_key])

            # Execute the update
            query = f"""
                UPDATE priorities
                SET {', '.join(update_fields)}
                WHERE id = ${param_count} AND user_key = ${param_count + 1}
                RETURNING *
            """

            updated_priority = await conn.fetchrow(query, *values)
            return updated_priority

    @staticmethod
    async def delete_priority(
        conn: asyncpg.Connection, priority_id: int, user_key: str
    ) -> bool:
        async with conn.transaction():
            db_priority = await conn.fetchrow(
                """
                SELECT p.*
                FROM priorities p
                WHERE p.id = $1
                AND p.user_key = $2
                """,
                priority_id,
                user_key,
            )

            if not db_priority:
                raise ValueError(f"Priority with id {priority_id} not found")

            await conn.execute(
                """
                DELETE FROM priorities p
                WHERE p.id = $1
                AND p.user_key = $2
                """,
                priority_id,
                user_key,
            )
            return True  # Successfully deleted

    @staticmethod
    async def get_total_priorities(conn: asyncpg.Connection, user_key: str) -> int:
        return await conn.fetchval(
            """
            SELECT COUNT(*)
            FROM priorities p
            WHERE p.user_key = $1
            """,
            user_key,
        )

    @staticmethod
    async def patch_priority(
        conn: asyncpg.Connection, priority_id: int, priority_patch: dict, user_key: str
    ) -> Priority:
        async with conn.transaction():
            db_priority = await conn.fetchrow(
                """
                SELECT p.*
                FROM priorities p
                WHERE p.id = $1
                AND p.user_key = $2
                """,
                priority_id,
                user_key,
            )
            if not db_priority:
                raise ValueError(f"Priority with id {priority_id} not found")

            for field, value in priority_patch.items():
                setattr(db_priority, field, value)
            updated_priority = await conn.execute(
                """
                UPDATE priorities p
                SET p.name = $1
                    , p.description = $2
                    , p.color = $3
                    , p.icon = $4
                    , p.order = $5
                WHERE p.id = $6
                AND p.user_key = $7
                RETURNING *
                """,
                db_priority.name,
                db_priority.description,
                db_priority.color,
                db_priority.icon,
                db_priority.order,
                db_priority.id,
                user_key,
            )
            return updated_priority

    @staticmethod
    async def check_availability(
        conn: asyncpg.Connection, priority: PriorityCreate, user_key: str
    ) -> tuple[bool, str]:
        async with conn.transaction():
            # Make sure the name is not already taken
            db_priority = await conn.fetchrow(
                """
                SELECT p.*
                FROM priorities p
                WHERE p.name = $1
                AND p.user_key = $2
                """,
                priority.name,
                user_key,
            )
            if db_priority:
                return False, "Name already taken"
            # Make sure the order is not already taken
            db_priority = await conn.fetchrow(
                """
                SELECT p.*
                FROM priorities p
                WHERE p.order = $1
                AND p.user_key = $2
                """,
                priority.order,
                user_key,
            )
            if db_priority:
                return False, "Order already taken"
            return True, "Available"
