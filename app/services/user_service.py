import uuid
import asyncpg
from app.core.security import PasswordHasher
from app.schemas.user import UserCreate, UserUpdate, UserUpdatePassword
from app.core.errors import AppError, NotFoundError


class UserService:
    @staticmethod
    async def get_users(
        conn: asyncpg.Connection, skip: int = 0, limit: int = 10
    ) -> list[asyncpg.Record]:
        try:
            resp = await conn.fetch(
                """
                SELECT u.*
                FROM users u
                LIMIT $1 OFFSET $2
                """,
                limit,
                skip,
            )
            if not resp:
                raise NotFoundError(ValueError("No users found"))
            return resp
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def get_user_by_key(conn: asyncpg.Connection, key: str) -> asyncpg.Record:
        try:
            resp = await conn.fetchrow(
                """
                SELECT u.*
                FROM users u
                WHERE u.key = $1
                """,
                key,
            )
            if not resp:
                raise NotFoundError(ValueError(f"User with key {key} not found"))
            return resp
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def get_user_by_email(conn: asyncpg.Connection, email: str) -> asyncpg.Record:
        try:
            resp = await conn.fetchrow(
                """
                SELECT u.*
                FROM users u
                WHERE u.email = $1
                """,
                email,
            )
            if not resp:
                raise NotFoundError(ValueError(f"User with email {email} not found"))
            return resp
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def get_user_by_username(
        conn: asyncpg.Connection, username: str
    ) -> asyncpg.Record:
        try:
            resp = await conn.fetchrow(
                """
                SELECT u.*
                FROM users u
                WHERE u.username = $1
                """,
                username,
            )
            if not resp:
                raise NotFoundError(
                    ValueError(f"User with username {username} not found")
                )
            return resp
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def create_user(conn: asyncpg.Connection, user: UserCreate) -> asyncpg.Record:
        async with conn.transaction():
            if await UserService.get_user_by_username(conn, user.username):
                raise ValueError(f"User with username {user.username} already exists")
            if await UserService.get_user_by_email(conn, user.email):
                raise ValueError(f"User with email {user.email} already exists")
            db_user = await conn.fetchrow(
                """
                INSERT INTO users u
                (u.key, u.name, u.username, u.email, u.hashed_password, u.is_active)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                str(uuid.uuid4()),
                user.name,
                user.username,
                user.email,
                PasswordHasher.hash(user.password),
                user.is_active,
            )
            return db_user

    @staticmethod
    async def update_user(
        conn: asyncpg.Connection, key: str, user: UserUpdate, user_key: str
    ) -> asyncpg.Record:
        async with conn.transaction():
            db_user = await UserService.get_user_by_key(conn, key)
            if not db_user:
                raise ValueError(f"User with key {key} not found")
            update_fields = []
            values = []
            param_count = 3
            values.append(db_user["id"])
            values.append(user_key)
            for field, value in user.model_dump().items():
                if value is not None:
                    update_fields.append(f'"{field}" = ${param_count}')
                    values.append(value)
                    param_count += 1
            if not update_fields:
                return db_user
            updated_user = await conn.fetchrow(
                f"""
                UPDATE users u
                SET {', '.join(update_fields)}
                WHERE u.id = ${param_count} AND u.key = ${param_count + 1}
                RETURNING *
                """,
                *values,
            )
            return updated_user

    @staticmethod
    async def delete_user(conn: asyncpg.Connection, key: str) -> bool:
        async with conn.transaction():
            db_user = await UserService.get_user_by_key(conn, key)
            if not db_user:
                raise ValueError(f"User with key {key} not found")
            await conn.execute(
                """
                DELETE FROM users u
                WHERE u.key = $1
                """,
                key,
            )
            return True

    @staticmethod
    async def get_total_users(conn: asyncpg.Connection) -> int:
        try:
            resp = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM users u
                """,
            )
            if not resp:
                raise NotFoundError(ValueError("No users found"))
            return resp
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def update_user_password(
        conn: asyncpg.Connection, key: str, user: UserUpdatePassword
    ):
        async with conn.transaction():
            db_user = await UserService.get_user_by_key(conn, key)
            if not db_user:
                raise ValueError(f"User with key {key} not found")
            if not PasswordHasher.verify(
                user.current_password, db_user["hashed_password"]
            ):
                raise ValueError("Current password is incorrect")
            db_user["hashed_password"] = PasswordHasher.hash(user.password)
            updated_user = await conn.fetchrow(
                """
                UPDATE users u
                SET u.hashed_password = $1
                WHERE u.key = $2
                RETURNING *
                """,
                db_user["hashed_password"],
                key,
            )
            return updated_user
