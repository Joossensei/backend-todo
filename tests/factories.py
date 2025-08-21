# tests/factories.py
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from faker import Faker
from app.core.security import TokenManager

fake = Faker()


class UserFactory:
    @staticmethod
    def create_user_data(**overrides) -> Dict[str, Any]:
        """Generate user data with sensible defaults"""
        data = {
            "key": str(uuid.uuid4()),
            "name": fake.name(),
            "username": fake.user_name(),
            "email": fake.email(),
            # Test123
            "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$OGJmOWEwMTA2NGU2ZTA4M2ZiODZlNjcwYjJjNjRiNjA1NmM3NmZjMDc4OWYwZjZjYjE5NDk3MGQ0YmE0MmUzZQ$sjsAfnZZeBW4Ifxb7AdFlNdpQGHFDsHQ8WazZEgPemU",
            "is_active": True,
        }
        data.update(overrides)
        return data

    @staticmethod
    async def create_user(conn, **overrides) -> Dict[str, Any]:
        """Insert user into DB and return the record"""
        user_data = UserFactory.create_user_data(**overrides)
        return await conn.fetchrow(
            """
            INSERT INTO users (key, name, username, email, hashed_password, is_active)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
            """,
            user_data["key"],
            user_data["name"],
            user_data["username"],
            user_data["email"],
            user_data["hashed_password"],
            user_data["is_active"],
        )


class PriorityFactory:
    @staticmethod
    def create_priority_data(user_key: str, **overrides) -> Dict[str, Any]:
        data = {
            "key": str(uuid.uuid4()),
            "name": fake.word().title(),
            "description": fake.sentence(),
            "color": fake.hex_color(),
            "icon": "fa-star",
            "order": fake.random_int(min=1, max=10),
            "user_key": user_key,
        }
        data.update(overrides)
        return data

    @staticmethod
    async def create_priority(conn, user_key: str, **overrides) -> Dict[str, Any]:
        priority_data = PriorityFactory.create_priority_data(user_key, **overrides)
        return await conn.fetchrow(
            """
            INSERT INTO priorities (key, name, description, color, icon, "order", user_key)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
            """,
            priority_data["key"],
            priority_data["name"],
            priority_data["description"],
            priority_data["color"],
            priority_data["icon"],
            priority_data["order"],
            user_key,
        )

    @staticmethod
    async def create_priorities_recursively(conn, user_key: str, count: int = 10):
        for i in range(count):
            await PriorityFactory.create_priority(
                conn, user_key, order=i + 1, name=f"Priority {i + 1}"
            )


class TodoFactory:
    @staticmethod
    def create_todo_data(
        user_key: str, priority_key: str, status_key: str, **overrides
    ) -> Dict[str, Any]:
        data = {
            "key": str(uuid.uuid4()),
            "title": fake.sentence(nb_words=3),
            "description": fake.paragraph(),
            "completed": False,
            "priority": priority_key,
            "user_key": user_key,
            "status": status_key,
        }
        data.update(overrides)
        return data

    @staticmethod
    async def create_todo(
        conn, user_key: str, priority_key: str, status_key: str, **overrides
    ) -> Dict[str, Any]:
        todo_data = TodoFactory.create_todo_data(
            user_key, priority_key, status_key, **overrides
        )
        return await conn.fetchrow(
            """
            INSERT INTO todos (key, title, description, completed, priority, user_key, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
            """,
            todo_data["key"],
            todo_data["title"],
            todo_data["description"],
            todo_data["completed"],
            todo_data["priority"],
            user_key,
            status_key,
        )


class AuthFactory:
    @staticmethod
    async def create_authenticated_user(conn, **user_overrides) -> Dict[str, Any]:
        """Create user and return auth data for testing"""
        user = await UserFactory.create_user(conn, **user_overrides)

        # Generate JWT token (you'll need to import your TokenManager)
        from app.core.security import TokenManager

        token = TokenManager.encode(
            {
                "sub": user["username"],
                "uid": user["key"],  # Add uid claim for rate limiting
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            }
        )

        return {
            "user": user,
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"},
        }

    @staticmethod
    async def get_auth_headers(conn, username: str) -> Dict[str, str]:
        """Get auth headers for existing user"""
        user = await conn.fetchrow("SELECT * FROM users WHERE username = $1", username)
        if not user:
            raise ValueError(f"User {username} not found")

        token = TokenManager.encode(
            {
                "sub": user["username"],
                "uid": user["key"],  # Add uid claim for rate limiting
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            }
        )

        return {"Authorization": f"Bearer {token}"}


class StatusFactory:
    @staticmethod
    def create_status_data(user_key: str, **overrides) -> Dict[str, Any]:
        data = {
            "key": str(uuid.uuid4()),
            "name": fake.word().title(),
            "description": fake.sentence(),
            "color": fake.hex_color(),
            "icon": "fa-star",
            "order": fake.random_int(min=1, max=10),
            "user_key": user_key,
            "is_default": False,
        }
        data.update(overrides)
        return data

    @staticmethod
    async def create_status(conn, user_key: str, **overrides) -> Dict[str, Any]:
        status_data = StatusFactory.create_status_data(user_key, **overrides)
        return await conn.fetchrow(
            """
            INSERT INTO statuses (key, name, description, color, icon, "order", user_key, is_default)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING *
            """,
            status_data["key"],
            status_data["name"],
            status_data["description"],
            status_data["color"],
            status_data["icon"],
            status_data["order"],
            user_key,
            status_data["is_default"],
        )

    @staticmethod
    async def create_statuses_recursively(conn, user_key: str, count: int = 10):
        for i in range(count):
            await StatusFactory.create_status(
                conn, user_key, order=i + 1, name=f"Status {i + 1}"
            )
