from app.schemas.todo import TodoCreate, TodoUpdate, TodoPatch
import uuid
from typing import Optional
import asyncpg
from app.core.errors import AppError, NotFoundError
import logging

logger = logging.getLogger(__name__)

ALLOWED_SORTS = {
    "incomplete-priority-desc": "t.completed ASC, p.order ASC, t.id DESC",
    "priority-desc": "p.order ASC, t.id DESC",
    "priority-desc-text-asc": "p.order ASC, t.title ASC",
    "text-asc": "t.title ASC, t.id DESC",
    "text-desc": "t.title DESC, t.id DESC",
    "created-desc": "t.id DESC",
}


class TodoService:
    @staticmethod
    async def create_todo(
        conn: asyncpg.Connection, todo: TodoCreate, user_key: str
    ) -> asyncpg.Record:
        async with conn.transaction():
            priority = await conn.fetchrow(
                """
                SELECT p.*
                FROM priorities p
                WHERE p.key = $1
                AND p.user_key = $2
                """,
                todo.priority,
                user_key,
            )
            if not priority:
                raise NotFoundError(f"Priority with key {todo.priority} not found")
            db_todo = {
                "key": str(uuid.uuid4()),
                "title": todo.title,
                "description": todo.description,
                "completed": todo.completed,
                "priority": priority["key"],
                "user_key": user_key,
            }
            db_todo = await conn.fetchrow(
                """
                INSERT INTO todos
                (key, title, description, completed, priority, user_key)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                db_todo["key"],
                db_todo["title"],
                db_todo["description"],
                db_todo["completed"],
                db_todo["priority"],
                db_todo["user_key"],
            )
            return db_todo

    @staticmethod
    async def fetch_todo_id_by_key(
        conn: asyncpg.Connection, key: str, user_key: str
    ) -> int:
        """Get a todo by its UUID key instead of ID."""
        try:
            db_todo = await conn.fetchrow(
                """
                SELECT t.id
                FROM todos t
                WHERE t.key = $1
                AND t.user_key = $2
                """,
                key,
                user_key,
            )
            if not db_todo:
                raise NotFoundError(f"Todo with key {key} not found")
            return db_todo["id"]
        except NotFoundError:
            raise
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def get_todos(
        conn: asyncpg.Connection,
        user_key: str,
        skip: int = 0,
        limit: int = 10,
        sort: str = "incomplete-priority-desc",
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[asyncpg.Record]:
        try:
            where = ["t.user_key = $1"]
            params = [user_key]
            next_idx = 2

            if completed is not None:
                where.append(f"t.completed = ${next_idx}")
                params.append(completed)
                next_idx += 1
            if priority is not None:
                where.append(f"t.priority = ${next_idx}")
                params.append(priority)
                next_idx += 1
            if search:
                where.append(f"t.title ILIKE ${next_idx}")
                params.append(f"%{search}%")
                next_idx += 1

            order_by = ALLOWED_SORTS.get(sort, ALLOWED_SORTS["created-desc"])
            sql = f"""
                    SELECT t.*
                    FROM todos t
                    LEFT JOIN priorities p ON p.key = t.priority
                    WHERE {' AND '.join(where)}
                    ORDER BY {order_by}
                    OFFSET ${next_idx} LIMIT ${next_idx + 1}
                    """
            params.extend([skip, limit])
            resp = await conn.fetch(sql, *params)
            return resp
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def get_todo(
        conn: asyncpg.Connection, todo_id: int, user_key: str
    ) -> asyncpg.Record:
        try:
            resp = await conn.fetchrow(
                """
                SELECT t.*
                FROM todos t
                WHERE t.id = $1
                AND t.user_key = $2
                """,
                todo_id,
                user_key,
            )
            if not resp:
                raise NotFoundError(f"Todo with id {todo_id} not found")
            return resp
        except NotFoundError:
            raise
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def get_total_todos(conn: asyncpg.Connection, user_key: str) -> int:
        try:
            resp = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM todos t
                WHERE t.user_key = $1
                """,
                user_key,
            )
            return resp
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def update_todo(
        conn: asyncpg.Connection, todo_id: int, todo_update: TodoUpdate, user_key: str
    ) -> asyncpg.Record:
        async with conn.transaction():
            priority = await conn.fetchrow(
                """
                SELECT p.*
                FROM priorities p
                WHERE p.key = $1
                AND p.user_key = $2
                """,
                todo_update.priority,
                user_key,
            )
            if not priority:
                raise NotFoundError(
                    f"Priority with id {todo_update.priority} not found"
                )
            todo_update.priority = priority["key"]
            db_todo = await conn.fetchrow(
                """
                SELECT t.*
                FROM todos t
                WHERE t.id = $1
                AND t.user_key = $2
                """,
                todo_id,
                user_key,
            )
            if db_todo:
                # Build dynamic update query
                update_fields = []
                values = []
                param_count = 1

                for field, value in todo_update.model_dump().items():
                    if field in ["title", "description", "completed", "priority"]:
                        update_fields.append(f'"{field}" = ${param_count}')
                        values.append(value)
                        param_count += 1

                if not update_fields:
                    # No valid fields to update
                    return db_todo

                # Add the WHERE clause parameters
                values.extend([todo_id, user_key])

                # Execute the update
                query = f"""
                    UPDATE todos
                    SET {', '.join(update_fields)}
                    WHERE id = ${param_count} AND user_key = ${param_count + 1}
                    RETURNING *
                """
                updated_todo = await conn.fetchrow(query, *values)
            return updated_todo

    @staticmethod
    async def delete_todo(
        conn: asyncpg.Connection, todo_id: int, user_key: str
    ) -> bool:
        async with conn.transaction():
            db_todo = await conn.fetchrow(
                """
                SELECT t.*
                FROM todos t
                WHERE t.id = $1
                AND t.user_key = $2
                """,
                todo_id,
                user_key,
            )

            if not db_todo:
                raise NotFoundError(f"Todo with id {todo_id} not found")

            await conn.execute(
                """
                DELETE FROM todos t
                WHERE t.id = $1
                AND t.user_key = $2
                """,
                todo_id,
                user_key,
            )
            return True  # Successfully deleted

    @staticmethod
    async def patch_todo(
        conn: asyncpg.Connection, todo_id: int, todo_patch: TodoPatch, user_key: str
    ) -> asyncpg.Record:
        async with conn.transaction():
            if todo_patch.priority is not None:
                priority = await conn.fetchrow(
                    """
                    SELECT p.*
                    FROM priorities p
                    WHERE p.key = $1
                    AND p.user_key = $2
                    """,
                    todo_patch.priority,
                    user_key,
                )
                if not priority:
                    raise NotFoundError(
                        f"Priority with id {todo_patch.priority} not found"
                    )
            db_todo = await conn.fetchrow(
                """
                SELECT t.*
                FROM todos t
                WHERE t.id = $1
                AND t.user_key = $2
                """,
                todo_id,
                user_key,
            )
            if not db_todo:
                raise NotFoundError(f"Todo with id {todo_id} not found")

            update_fields = []
            values = []
            param_count = 3
            values.append(db_todo["id"])
            values.append(user_key)
            for field, value in todo_patch.model_dump().items():
                if value is not None:
                    update_fields.append(f'"{field}" = ${param_count}')
                    values.append(value)
                    param_count += 1
            query = f"""
                UPDATE todos
                SET {', '.join(update_fields)}
                WHERE id = $1 AND user_key = $2
                RETURNING *
            """
            updated_todo = await conn.fetchrow(query, *values)
            return updated_todo
