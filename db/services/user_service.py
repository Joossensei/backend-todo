import uuid
import asyncpg
from app.core.security import PasswordHasher
from app.schemas.user import UserCreate, UserUpdate, UserUpdatePassword


class UserService:
    @staticmethod
    async def get_users(conn: asyncpg.Connection, skip: int = 0, limit: int = 10):
        return await conn.fetch(
            "SELECT * FROM users LIMIT $1 OFFSET $2",
            limit,
            skip,
        )

    @staticmethod
    async def get_user_by_key(conn: asyncpg.Connection, key: str):
        return await conn.fetchrow(
            "SELECT * FROM users WHERE key = $1",
            key,
        )

    @staticmethod
    async def get_user_by_email(conn: asyncpg.Connection, email: str):
        return await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            email,
        )

    @staticmethod
    async def get_user_by_username(conn: asyncpg.Connection, username: str):
        return await conn.fetchrow(
            "SELECT * FROM users WHERE username = $1",
            username,
        )

    @staticmethod
    async def create_user(conn: asyncpg.Connection, user: UserCreate):
        if await UserService.get_user_by_username(conn, user.username):
            raise ValueError(f"User with username {user.username} already exists")
        if await UserService.get_user_by_email(conn, user.email):
            raise ValueError(f"User with email {user.email} already exists")
        db_user = await conn.fetchrow(
            "INSERT INTO users (key, name, username, email, hashed_password, is_active) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *",
            str(uuid.uuid4()),
            user.name,
            user.username,
            user.email,
            PasswordHasher.hash(user.password),
            user.is_active,
        )
        return db_user

    @staticmethod
    async def update_user(conn: asyncpg.Connection, key: str, user: UserUpdate):
        db_user = await UserService.get_user_by_key(conn, key)
        if not db_user:
            raise ValueError(f"User with key {key} not found")
        if user.name is not None:
            db_user["name"] = user.name
        if user.email is not None:
            db_user["email"] = user.email
        if user.is_active is not None:
            db_user["is_active"] = user.is_active
        await conn.execute(
            "UPDATE users SET name = $1, email = $2, is_active = $3 WHERE key = $4",
            db_user["name"],
            db_user["email"],
            db_user["is_active"],
            key,
        )
        return db_user

    @staticmethod
    async def delete_user(conn: asyncpg.Connection, key: str):
        db_user = await UserService.get_user_by_key(conn, key)
        if not db_user:
            raise ValueError(f"User with key {key} not found")
        await conn.execute("DELETE FROM users WHERE key = $1", key)
        return True

    @staticmethod
    async def get_total_users(conn: asyncpg.Connection):
        return await conn.fetchval("SELECT COUNT(*) FROM users")

    @staticmethod
    async def update_user_password(
        conn: asyncpg.Connection, key: str, user: UserUpdatePassword
    ):
        db_user = await UserService.get_user_by_key(conn, key)
        if not db_user:
            raise ValueError(f"User with key {key} not found")
        if not PasswordHasher.verify(user.current_password, db_user.hashed_password):
            raise ValueError("Current password is incorrect")
        db_user["hashed_password"] = PasswordHasher.hash(user.password)
        await conn.execute(
            "UPDATE users SET hashed_password = $1 WHERE key = $2",
            db_user["hashed_password"],
            key,
        )
        return db_user
