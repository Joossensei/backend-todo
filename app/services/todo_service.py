# app/services/todo_service.py
import asyncpg
from app.schemas.todo import TodoCreate, TodoUpdate
import uuid
from typing import Optional, List, Dict, Any


class TodoService:
    @staticmethod
    async def create_todo(
        connection: asyncpg.Connection, todo: TodoCreate, user_key: str
    ) -> Dict[str, Any]:
        """Create a new todo using raw SQL."""
        # First check if priority exists
        priority_data = await connection.fetchrow(
            "SELECT key FROM priorities WHERE key = $1 AND user_key = $2",
            todo.priority,
            user_key,
        )
        if not priority_data:
            raise ValueError(f"Priority with key {todo.priority} not found")

        # Create todo
        todo_key = str(uuid.uuid4())
        todo_data = await connection.fetchrow(
            """
            INSERT INTO todos (key, title, description, completed, priority, user_key)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, key, title, description, completed, priority, user_key, created_at, updated_at
        """,
            todo_key,
            todo.title,
            todo.description,
            todo.completed,
            todo.priority,
            user_key,
        )

        return dict(todo_data)

    @staticmethod
    async def get_todo_by_key(
        connection: asyncpg.Connection, key: str, user_key: str
    ) -> Optional[Dict[str, Any]]:
        """Get a todo by its UUID key."""
        todo_data = await connection.fetchrow(
            """
            SELECT id, key, title, description, completed, priority, user_key, created_at, updated_at
            FROM todos 
            WHERE key = $1 AND user_key = $2
        """,
            key,
            user_key,
        )

        if not todo_data:
            return None

        return dict(todo_data)

    @staticmethod
    async def get_todos(
        connection: asyncpg.Connection,
        user_key: str,
        skip: int = 0,
        limit: int = 10,
        sort: str = "incomplete-priority-desc",
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get todos with filtering and sorting."""
        # Build WHERE clause
        where_conditions = ["user_key = $1"]
        params = [user_key]
        param_count = 1

        if completed is not None:
            param_count += 1
            where_conditions.append(f"completed = ${param_count}")
            params.append(completed)

        if priority is not None:
            param_count += 1
            where_conditions.append(f"priority = ${param_count}")
            params.append(priority)

        if search is not None:
            param_count += 1
            where_conditions.append(f"LOWER(title) LIKE LOWER(${param_count})")
            params.append(f"%{search}%")

        where_clause = " AND ".join(where_conditions)

        # Build ORDER BY clause
        if sort == "priority-desc":
            order_clause = """
                ORDER BY (
                    SELECT p.order FROM priorities p 
                    WHERE p.key = todos.priority AND p.user_key = $1
                ) ASC
            """
        elif sort == "priority-desc-text-asc":
            order_clause = """
                ORDER BY (
                    SELECT p.order FROM priorities p 
                    WHERE p.key = todos.priority AND p.user_key = $1
                ) ASC, title ASC
            """
        elif sort == "incomplete-priority-desc":
            order_clause = """
                ORDER BY completed ASC, (
                    SELECT p.order FROM priorities p 
                    WHERE p.key = todos.priority AND p.user_key = $1
                ) ASC
            """
        elif sort == "text-asc":
            order_clause = "ORDER BY title ASC"
        elif sort == "text-desc":
            order_clause = "ORDER BY title DESC"
        else:
            order_clause = "ORDER BY id DESC"

        # Build final query
        query = f"""
            SELECT id, key, title, description, completed, priority, user_key, created_at, updated_at
            FROM todos 
            WHERE {where_clause}
            {order_clause}
            LIMIT ${param_count + 1} OFFSET ${param_count + 2}
        """
        params.extend([limit, skip])

        todos_data = await connection.fetch(query, *params)
        return [dict(todo) for todo in todos_data]

    @staticmethod
    async def get_total_todos(connection: asyncpg.Connection, user_key: str) -> int:
        """Get total count of todos for a user."""
        result = await connection.fetchval(
            "SELECT COUNT(*) FROM todos WHERE user_key = $1", user_key
        )
        return result

    @staticmethod
    async def update_todo(
        connection: asyncpg.Connection, key: str, todo_update: TodoUpdate, user_key: str
    ) -> Optional[Dict[str, Any]]:
        """Update a todo."""
        # Check if priority exists
        if todo_update.priority:
            priority_data = await connection.fetchrow(
                "SELECT key FROM priorities WHERE key = $1", todo_update.priority
            )
            if not priority_data:
                raise ValueError(f"Priority with key {todo_update.priority} not found")

        # Build update query dynamically
        update_fields = []
        params = []
        param_count = 0

        if todo_update.title is not None:
            param_count += 1
            update_fields.append(f"title = ${param_count}")
            params.append(todo_update.title)

        if todo_update.description is not None:
            param_count += 1
            update_fields.append(f"description = ${param_count}")
            params.append(todo_update.description)

        if todo_update.completed is not None:
            param_count += 1
            update_fields.append(f"completed = ${param_count}")
            params.append(todo_update.completed)

        if todo_update.priority is not None:
            param_count += 1
            update_fields.append(f"priority = ${param_count}")
            params.append(todo_update.priority)

        if not update_fields:
            # No fields to update, just return the current todo
            return await TodoService.get_todo_by_key(connection, key, user_key)

        # Add key and user_key to params
        param_count += 1
        update_fields.append("updated_at = NOW()")
        params.extend([key, user_key])

        query = f"""
            UPDATE todos 
            SET {', '.join(update_fields)}
            WHERE key = ${param_count} AND user_key = ${param_count + 1}
            RETURNING id, key, title, description, completed, priority, user_key, created_at, updated_at
        """

        todo_data = await connection.fetchrow(query, *params)
        if not todo_data:
            return None

        return dict(todo_data)

    @staticmethod
    async def patch_todo(
        connection: asyncpg.Connection, key: str, todo_patch: dict, user_key: str
    ) -> Optional[Dict[str, Any]]:
        """Patch a todo with partial updates."""
        # Build update query dynamically
        update_fields = []
        params = []
        param_count = 0

        for field, value in todo_patch.items():
            if field in ["title", "description", "completed", "priority"]:
                param_count += 1
                update_fields.append(f"{field} = ${param_count}")
                params.append(value)

        if not update_fields:
            # No valid fields to update, just return the current todo
            return await TodoService.get_todo_by_key(connection, key, user_key)

        # Add key and user_key to params
        param_count += 1
        update_fields.append("updated_at = NOW()")
        params.extend([key, user_key])

        query = f"""
            UPDATE todos 
            SET {', '.join(update_fields)}
            WHERE key = ${param_count} AND user_key = ${param_count + 1}
            RETURNING id, key, title, description, completed, priority, user_key, created_at, updated_at
        """

        todo_data = await connection.fetchrow(query, *params)
        if not todo_data:
            return None

        return dict(todo_data)

    @staticmethod
    async def delete_todo(
        connection: asyncpg.Connection, key: str, user_key: str
    ) -> bool:
        """Delete a todo."""
        result = await connection.execute(
            "DELETE FROM todos WHERE key = $1 AND user_key = $2", key, user_key
        )
        return result == "DELETE 1"
