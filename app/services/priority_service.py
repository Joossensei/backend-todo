# app/services/priority_service.py
from app.models.priority import Priority
from app.schemas.priority import (
    PriorityCreate,
    PriorityPatch,
    PriorityUpdate,
    PriorityReorder,
)
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
            # Dynamic
            update_fields = []
            values = []
            param_count = 1
            for field, value in priority_patch.model_dump().items():
                if value is not None:
                    update_fields.append(f'"{field}" = ${param_count}')
                    values.append(value)
                    param_count += 1
            if not update_fields:
                raise ValidationError(custom_message="No valid fields to update")
            # Add the WHERE clause parameters
            values.extend([priority_id, user_key])
            # Execute the update
            query = f"""
                UPDATE priorities
                SET {', '.join(update_fields)}
                WHERE id = ${param_count} AND user_key = ${param_count + 1}
                RETURNING *
                """
            try:
                updated_priority = await conn.fetchrow(query, *values)
            except asyncpg.exceptions.UniqueViolationError as e:
                raise ValidationError(custom_message=e.message)
            except Exception as e:
                raise AppError(e)
            return updated_priority

    @staticmethod
    async def reorder_priorities(
        conn: asyncpg.Connection, reorder_data: PriorityReorder, user_key: str
    ) -> list[Priority]:
        """
        Reorder priorities by moving a priority from one order position to another.
        This method handles the unique constraint on (user_key, order) by temporarily
        using negative order values during the reordering process.
        """
        async with conn.transaction():
            from_order = reorder_data.fromOrder
            to_order = reorder_data.toOrder

            # Validate that the from_order exists for this user
            existing_priority = await conn.fetchrow(
                """
                SELECT id, "order" FROM priorities
                WHERE user_key = $1 AND "order" = $2
                """,
                user_key,
                from_order,
            )

            if not existing_priority:
                raise NotFoundError(
                    f"Priority with order {from_order} not found for user"
                )

            # Get all priorities for this user ordered by current order
            priorities = await conn.fetch(
                """
                SELECT id, "order" FROM priorities
                WHERE user_key = $1
                ORDER BY "order" ASC
                """,
                user_key,
            )

            if not priorities:
                raise NotFoundError("No priorities found for user")

            # Validate to_order is within valid range
            max_order = len(priorities)
            if to_order < 1 or to_order > max_order:
                raise ValidationError(
                    custom_message=f"Target order must be between 1 and {max_order}"
                )

            # If from_order equals to_order, no reordering needed
            if from_order == to_order:
                return await PriorityService.get_priorities(conn, user_key, 0, 1000)

            # Create a mapping of current order to priority ID
            order_to_id = {p["order"]: p["id"] for p in priorities}

            # Create the new order sequence
            current_orders = list(range(1, max_order + 1))

            # Remove the from_order and insert it at the to_order position
            current_orders.remove(from_order)
            current_orders.insert(to_order - 1, from_order)

            # Create a mapping of priority ID to new order
            id_to_new_order = {}
            for i, order in enumerate(current_orders):
                priority_id = order_to_id[order]
                id_to_new_order[priority_id] = i + 1

            # Update all priorities with new order values
            # Use temporary negative values to avoid constraint violations
            for priority in priorities:
                temp_order = -(priority["id"])  # Use negative ID as temporary
                await conn.execute(
                    """
                    UPDATE priorities
                    SET "order" = $1
                    WHERE id = $2 AND user_key = $3
                    """,
                    temp_order,
                    priority["id"],
                    user_key,
                )

            # Now update with the final order values
            for priority in priorities:
                final_order = id_to_new_order[priority["id"]]
                await conn.execute(
                    """
                    UPDATE priorities
                    SET "order" = $1
                    WHERE id = $2 AND user_key = $3
                    """,
                    final_order,
                    priority["id"],
                    user_key,
                )

            # Return the updated priorities
            return await PriorityService.get_priorities(conn, user_key, 0, 1000)
