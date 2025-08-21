# app/services/status_service.py
import uuid
import asyncpg
from app.core.errors import AppError, NotFoundError, ValidationError
import logging
from app.schemas import (
    StatusCreate,
    StatusUpdate,
    StatusPatch,
    StatusReorder,
)
from app.models import Status

logger = logging.getLogger(__name__)


class StatusService:
    @staticmethod
    async def create_status(
        conn: asyncpg.Connection, status: StatusCreate, user_key: str
    ) -> Status:
        async with conn.transaction():
            status_key = str(uuid.uuid4())
            db_status = await conn.fetchrow(
                """
                INSERT INTO statuses
                        ( "key"
                        , "name"
                        , "description"
                        , "user_key"
                        , "order"
                        , "color"
                        , "icon"
                        , "is_default")
                    VALUES ( $1
                            , $2
                            , $3
                            , $4
                            , $5
                            , $6
                            , $7
                            , $8
                            ) RETURNING *
                """,
                status_key,
                status.name,
                status.description,
                user_key,
                status.order,
                status.color,
                status.icon,
                status.is_default,
            )
            return db_status

    @staticmethod
    async def fetch_status_id_by_key(
        conn: asyncpg.Connection, key: str, user_key: str
    ) -> int:
        """Get a priority by its UUID key instead of ID."""
        try:
            db_status = await conn.fetchrow(
                """
                SELECT s.id
            FROM statuses s
            WHERE s.key = $1
            AND s.user_key = $2
            """,
                key,
                user_key,
            )
            if not db_status:
                raise NotFoundError(f"Status with key {key} not found")
            return db_status["id"]
        except NotFoundError:
            raise
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def get_statuses(
        conn: asyncpg.Connection, user_key: str, skip: int = 0, limit: int = 10
    ) -> list[Status]:
        try:
            resp = await conn.fetch(
                """
                SELECT s.*
                FROM statuses s
                WHERE s.user_key = $1
                ORDER BY s.order ASC
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
    async def get_status(
        conn: asyncpg.Connection, status_id: int, user_key: str
    ) -> Status:
        try:
            resp = await conn.fetchrow(
                """
                SELECT s.*
                FROM statuses s
                WHERE s.id = $1
                AND s.user_key = $2
                """,
                status_id,
                user_key,
            )
            if not resp:
                raise NotFoundError(ValueError(f"Status with id {status_id} not found"))
            return resp
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def update_status(
        conn: asyncpg.Connection,
        status_id: int,
        status_update: StatusUpdate,
        user_key: str,
    ) -> Status:
        async with conn.transaction():
            # First check if status exists
            db_status = await conn.fetchrow(
                """
                SELECT s.*
                FROM statuses s
                WHERE s.id = $1
                AND s.user_key = $2
                """,
                status_id,
                user_key,
            )
            if not db_status:
                raise NotFoundError(f"Status with id {status_id} not found")

            # Build dynamic update query
            update_fields = []
            values = []
            param_count = 1

            for field, value in status_update.model_dump().items():
                if field in ["name", "description", "color", "icon", "order"]:
                    update_fields.append(f'"{field}" = ${param_count}')
                    values.append(value)
                    param_count += 1

            if not update_fields:
                # No valid fields to update
                return db_status

            # Add the WHERE clause parameters
            values.extend([status_id, user_key])

            # Execute the update
            query = f"""
                UPDATE statuses
                SET {', '.join(update_fields)}
                WHERE id = ${param_count} AND user_key = ${param_count + 1}
                RETURNING *
                """

            updated_status = await conn.fetchrow(query, *values)
            return updated_status

    @staticmethod
    async def delete_status(
        conn: asyncpg.Connection, status_id: int, user_key: str
    ) -> bool:
        async with conn.transaction():
            db_status = await conn.fetchrow(
                """
                SELECT s.*
                FROM statuses s
                WHERE s.id = $1
                AND s.user_key = $2
                """,
                status_id,
                user_key,
            )

            if not db_status:
                raise NotFoundError(f"Status with id {status_id} not found")

            await conn.execute(
                """
                DELETE FROM statuses s
                WHERE s.id = $1
                AND s.user_key = $2
                """,
                status_id,
                user_key,
            )
            return True  # Successfully deleted

    @staticmethod
    async def get_total_statuses(conn: asyncpg.Connection, user_key: str) -> int:
        try:
            resp = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM statuses s
                WHERE s.user_key = $1
                """,
                user_key,
            )
            # COUNT(*) returns 0 for empty sets; return that instead of raising
            return int(resp or 0)
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def patch_status(
        conn: asyncpg.Connection,
        status_id: int,
        status_patch: StatusPatch,
        user_key: str,
    ) -> Status:
        async with conn.transaction():
            db_status = await conn.fetchrow(
                """
                SELECT s.*
                FROM statuses s
                WHERE s.id = $1
                AND s.user_key = $2
                """,
                status_id,
                user_key,
            )
            if not db_status:
                raise NotFoundError(f"Status with id {status_id} not found")
            # Dynamic
            update_fields = []
            values = []
            param_count = 1
            for field, value in status_patch.model_dump().items():
                if value is not None:
                    update_fields.append(f'"{field}" = ${param_count}')
                    values.append(value)
                    param_count += 1
            if not update_fields:
                raise ValidationError(custom_message="No valid fields to update")
            # Add the WHERE clause parameters
            values.extend([status_id, user_key])
            # Execute the update
            query = f"""
                UPDATE statuses
                SET {', '.join(update_fields)}
                WHERE id = ${param_count} AND user_key = ${param_count + 1}
                RETURNING *
                """
            try:
                updated_status = await conn.fetchrow(query, *values)
            except asyncpg.exceptions.UniqueViolationError as e:
                raise ValidationError(custom_message=e.message)
            except Exception as e:
                raise AppError(e)
            return updated_status

    @staticmethod
    async def reorder_statuses(
        conn: asyncpg.Connection, reorder_data: StatusReorder, user_key: str
    ) -> list[Status]:
        """
        Reorder statuses by moving a status from one order position to another.
        This method handles the unique constraint on (user_key, order) by temporarily
        using negative order values during the reordering process.
        """
        async with conn.transaction():
            from_order = reorder_data.fromOrder
            to_order = reorder_data.toOrder

            # Validate that the from_order exists for this user
            existing_status = await conn.fetchrow(
                """
                SELECT id, "order" FROM statuses
                WHERE user_key = $1 AND "order" = $2
                """,
                user_key,
                from_order,
            )

            if not existing_status:
                raise NotFoundError(
                    f"Status with order {from_order} not found for user"
                )

            # Get all statuses for this user ordered by current order
            statuses = await conn.fetch(
                """
                SELECT id, "order" FROM statuses
                WHERE user_key = $1
                ORDER BY "order" ASC
                """,
                user_key,
            )

            if not statuses:
                raise NotFoundError("No statuses found for user")

            # Validate to_order is within valid range
            max_order = len(statuses)
            if to_order < 1 or to_order > max_order:
                raise ValidationError(
                    custom_message=f"Target order must be between 1 and {max_order}"
                )

            # If from_order equals to_order, no reordering needed
            if from_order == to_order:
                return await StatusService.get_statuses(conn, user_key, 0, 1000)

            # Create a mapping of current order to status ID
            order_to_id = {p["order"]: p["id"] for p in statuses}

            # Create the new order sequence
            current_orders = list(range(1, max_order + 1))

            # Remove the from_order and insert it at the to_order position
            current_orders.remove(from_order)
            current_orders.insert(to_order - 1, from_order)

            # Create a mapping of priority ID to new order
            id_to_new_order = {}
            for i, order in enumerate(current_orders):
                status_id = order_to_id[order]
                id_to_new_order[status_id] = i + 1

            # Update all priorities with new order values
            # Use temporary negative values to avoid constraint violations
            for status in statuses:
                temp_order = -(status["id"])  # Use negative ID as temporary
                await conn.execute(
                    """
                    UPDATE statuses
                    SET "order" = $1
                    WHERE id = $2 AND user_key = $3
                    """,
                    temp_order,
                    status["id"],
                    user_key,
                )

            # Now update with the final order values
            for status in statuses:
                final_order = id_to_new_order[status["id"]]
                await conn.execute(
                    """
                    UPDATE statuses
                    SET "order" = $1
                    WHERE id = $2 AND user_key = $3
                    """,
                    final_order,
                    status["id"],
                    user_key,
                )

            # Return the updated statuses
            return await StatusService.get_statuses(conn, user_key, 0, 1000)
