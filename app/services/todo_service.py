# app/services/todo_service.py
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate
import uuid
from typing import Optional
import asyncpg


class TodoService:
    @staticmethod
    async def create_todo(
        conn: asyncpg.Connection, todo: TodoCreate, user_key: str
    ) -> Todo:
        async with conn.transaction():
            priority = await conn.fetchrow(
                """
                SELECT p.*
                FROM priorities p
                WHERE p.key = $1
                AND p.user_key = $2
                """,
                todo["priority"],
                user_key,
            )
            if not priority:
                raise ValueError(f"Priority with key {todo['priority']} not found")
            db_todo = {
                "key": str(uuid.uuid4()),
                "title": todo["title"],
                "description": todo["description"],
                "completed": todo["completed"],
                "priority": priority["key"],
                "user_key": user_key,
            }
            db_todo = await conn.fetchrow(
                """
                INSERT INTO todos t
                (t.key, t.title, t.description, t.completed, t.priority, t.user_key)
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
        db_todo = await conn.fetchrow(
            """
            SELECT t.*
            FROM todos t
            WHERE t.key = $1
            AND t.user_key = $2
            """,
            key,
            user_key,
        )
        if not db_todo:
            raise ValueError(f"Todo with key {key} not found for user {user_key}")
        return db_todo["id"] if db_todo else None

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
    ):
        query = await conn.fetch(
            """
            SELECT t.*
            FROM todos t
            WHERE t.user_key = $1
            OFFSET $2
            LIMIT $3
            """,
            user_key,
            skip,
            limit,
        )
        if completed is not None:
            query = await conn.fetch(
                """
                SELECT t.*
                FROM todos t
                WHERE t.user_key = $1 AND t.completed = $2
                """,
                user_key,
                completed,
            )
        if priority is not None:
            query = await conn.fetch(
                """
                SELECT t.*
                FROM todos t
                WHERE t.user_key = $1 AND t.priority = $2
                """,
                user_key,
                priority,
            )
        if search is not None:
            query = await conn.fetch(
                """
                SELECT t.*
                FROM todos t
                WHERE t.user_key = $1 AND t.title ILIKE $2
                """,
                user_key,
                f"%{search.lower()}%",
            )

        # Sorting on priority is on priority table with column "order"

        if sort == "priority-desc":
            query = await conn.fetch(
                """
                SELECT t.*
                FROM todos t
                JOIN priorities p ON t.priority = p.key
                WHERE t.user_key = $1
                ORDER BY p.order DESC
                LIMIT $2 OFFSET $3
                """,
                user_key,
                limit,
                skip,
            )
        elif sort == "priority-desc-text-asc":
            query = await conn.fetch(
                """
                SELECT t.*
                FROM todos t
                JOIN priorities p ON t.priority = p.key
                WHERE t.user_key = $1
                ORDER BY p.order DESC, t.title ASC
                LIMIT $2 OFFSET $3
                """,
                user_key,
                limit,
                skip,
            )
        elif sort == "incomplete-priority-desc":
            query = await conn.fetch(
                """
                SELECT t.*
                FROM todos t
                JOIN priorities p ON t.priority = p.key
                WHERE t.user_key = $1
                ORDER BY t.completed, p.order ASC
                LIMIT $2 OFFSET $3
                """,
                user_key,
                limit,
                skip,
            )
        elif sort == "text-asc":
            query = await conn.fetch(
                """
                SELECT t.*
                FROM todos t
                WHERE t.user_key = $1
                ORDER BY t.title ASC
                LIMIT $2 OFFSET $3
                """,
                user_key,
                limit,
                skip,
            )
        elif sort == "text-desc":
            query = await conn.fetch(
                """
                SELECT t.*
                FROM todos t
                WHERE t.user_key = $1
                ORDER BY t.title DESC
                LIMIT $2 OFFSET $3
                """,
                user_key,
                limit,
                skip,
            )
        else:
            query = await conn.fetch(
                """
                SELECT t.*
                FROM todos t
                WHERE t.user_key = $1
                ORDER BY t.id DESC
                LIMIT $2 OFFSET $3
                """,
                user_key,
                limit,
                skip,
            )

        return query

    @staticmethod
    async def get_todo(conn: asyncpg.Connection, todo_id: int, user_key: str):
        return await conn.fetchrow(
            """
            SELECT t.*
            FROM todos t
            WHERE t.id = $1
            AND t.user_key = $2
            """,
            todo_id,
            user_key,
        )

    @staticmethod
    async def update_todo(
        conn: asyncpg.Connection, todo_id: int, todo_update: TodoUpdate, user_key: str
    ):
        async with conn.transaction():
            priority = await conn.fetchrow(
                """
                SELECT p.*
                FROM priorities p
                WHERE p.key = $1
                AND p.user_key = $2
                """,
                todo_update["priority"],
                user_key,
            )
            if not priority:
                raise ValueError(
                    f"Priority with id {todo_update['priority']} not found"
                )
            todo_update["priority"] = priority["key"]
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

                for field, value in todo_update.items():
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
                raise ValueError(f"Todo with id {todo_id} not found")

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
    async def get_total_todos(conn: asyncpg.Connection, user_key: str) -> int:
        return await conn.fetchval(
            """
            SELECT COUNT(*)
            FROM todos t
            WHERE t.user_key = $1
            """,
            user_key,
        )

    @staticmethod
    async def patch_todo(
        conn: asyncpg.Connection, todo_id: int, todo_patch: dict, user_key: str
    ) -> Todo:
        async with conn.transaction():
            if "priority" in todo_patch:
                priority = await conn.fetchrow(
                    """
                    SELECT p.*
                    FROM priorities p
                    WHERE p.key = $1
                    AND p.user_key = $2
                    """,
                    todo_patch["priority"],
                    user_key,
                )
                if not priority:
                    raise ValueError(
                        f"Priority with id {todo_patch['priority']} not found"
                    )
                todo_patch["priority"] = priority["key"]
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
                raise ValueError(f"Todo with id {todo_id} not found")
            updated_todo = {}
            for field, value in todo_patch.items():
                if field == "priority":
                    updated_todo[field] = priority["key"]
                else:
                    updated_todo[field] = value
            # Update the todo using conditional query
            update_fields = []
            values = []
            param_count = 3
            values.append(db_todo["id"])
            values.append(user_key)
            for field, value in todo_patch.items():
                if field == "priority":
                    update_fields.append(f'"{field}" = ${param_count}')
                    values.append(priority["key"])
                else:
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
