# app/services/priority_service.py
from app.models.priority import Priority
from app.schemas.priority import PriorityCreate, PriorityPatch, PriorityUpdate
import uuid
import asyncpg
from app.core.errors import AppError, NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)


class PriorityService:
    @staticmethod
    async def create_priority(
        conn: asyncpg.Connection, priority: PriorityCreate, user_key: str
    ) -> Priority:
        async with conn.transaction():
            priority_key = str(uuid.uuid4())
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
                priority_key,
                priority.name,
                priority.description,
                priority.color,
                priority.icon,
                priority.order,
                user_key,
            )
            return db_priority

    @staticmethod
    async def fetch_priority_id_by_key(
        conn: asyncpg.Connection, key: str, user_key: str
    ) -> int:
        """Get a priority by its UUID key instead of ID."""
        try:
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
            if not db_priority:
                raise NotFoundError(f"Priority with key {key} not found")
            return db_priority["id"]
        except NotFoundError:
            raise
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def get_priorities(
        conn: asyncpg.Connection, user_key: str, skip: int = 0, limit: int = 10
    ) -> list[Priority]:
        try:
            resp = await conn.fetch(
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
            return resp
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def get_priority(
        conn: asyncpg.Connection, priority_id: int, user_key: str
    ) -> Priority:
        try:
            resp = await conn.fetchrow(
                """
                SELECT p.*
                FROM priorities p
                WHERE p.id = $1
                AND p.user_key = $2
                """,
                priority_id,
                user_key,
            )
            if not resp:
                raise NotFoundError(
                    ValueError(f"Priority with id {priority_id} not found")
                )
            return resp
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def update_priority(
        conn: asyncpg.Connection,
        priority_id: int,
        priority_update: PriorityUpdate,
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
                raise NotFoundError(f"Priority with id {priority_id} not found")

            # Build dynamic update query
            update_fields = []
            values = []
            param_count = 1

            for field, value in priority_update.model_dump().items():
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
                raise NotFoundError(f"Priority with id {priority_id} not found")

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
        try:
            resp = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM priorities p
                WHERE p.user_key = $1
                """,
                user_key,
            )
            # COUNT(*) returns 0 for empty sets; return that instead of raising
            return int(resp or 0)
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def patch_priority(
        conn: asyncpg.Connection,
        priority_id: int,
        priority_patch: PriorityPatch,
        user_key: str,
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
                raise NotFoundError(f"Priority with id {priority_id} not found")
            logger.info("Check 233")
            # Dynamic
            update_fields = []
            values = []
            param_count = 1
            logger.info("Check 238")
            logger.info("Model Dump items:")
            logger.info(priority_patch.model_dump())
            for field, value in priority_patch.model_dump().items():
                if value is not None:
                    update_fields.append(f'"{field}" = ${param_count}')
                    values.append(value)
                    param_count += 1
            if not update_fields:
                raise ValidationError(custom_message="No valid fields to update")
            # Add the WHERE clause parameters
            values.extend([priority_id, user_key])
            logger.info("Check 247")
            # Execute the update
            query = f"""
                UPDATE priorities
                SET {', '.join(update_fields)}
                WHERE id = ${param_count} AND user_key = ${param_count + 1}
                RETURNING *
                """
            logger.info("Check 255")
            updated_priority = await conn.fetchrow(query, *values)
            return updated_priority
