import uuid
import asyncpg
from app.core.security import PasswordHasher
from app.schemas.user import UserCreate, UserUpdate, UserUpdatePassword
from app.core.errors import AppError, NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)


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
                raise NotFoundError(f"User with key {key} not found")
            return resp
        except NotFoundError:
            raise
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
            return resp
        except Exception as e:
            raise AppError(e)

    @staticmethod
    async def create_user(conn: asyncpg.Connection, user: UserCreate) -> asyncpg.Record:
        async with conn.transaction():
            if await UserService.get_user_by_username(conn, user.username):
                raise ValidationError(
                    f"User with username {user.username} already exists"
                )
            if await UserService.get_user_by_email(conn, user.email):
                raise ValidationError(f"User with email {user.email} already exists")
            db_user = await conn.fetchrow(
                """
                INSERT INTO users
                (key, name, username, email, hashed_password, is_active)
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
                raise NotFoundError(f"User with key {key} not found")
            param_count = 1
            update_fields = []
            update_values = []
            for field, value in user.model_dump().items():
                update_fields.append(f'"{field}" = ${param_count}')
                update_values.append(value)
                param_count += 1
            update_values.append(db_user["id"])
            update_values.append(user_key)
            sql = f"""
            UPDATE users u
            SET {', '.join(update_fields)}
            WHERE u.id = ${param_count} AND u.key = ${param_count + 1}
            RETURNING *
            """
            updated_user = await conn.fetchrow(
                sql,
                *update_values,
            )
            return updated_user

    @staticmethod
    async def patch_user(conn: asyncpg.Connection, key: str, user: UserUpdate, user_key: str) -> asyncpg.Record:
        async with conn.transaction():
            db_user = await UserService.get_user_by_key(conn, key)
            if not db_user:
                raise NotFoundError(f"User with key {key} not found")
            param_count = 3
            update_fields = []
            update_values = []
            update_values.append(db_user["id"])
            update_values.append(key)
            for field, value in user.model_dump().items():
                if value is not None:
                    update_fields.append(f'"{field}" = ${param_count}')
                    update_values.append(value)
                    param_count += 1
            sql = f"""
            UPDATE users u
            SET {', '.join(update_fields)}
            WHERE u.id = $1 AND u.key = $2
            RETURNING *
            """
            updated_user = await conn.fetchrow(sql, *update_values)
            logger.info(f"Updated user: {updated_user}")
            return updated_user

    @staticmethod
    async def delete_user(conn: asyncpg.Connection, key: str) -> bool:
        async with conn.transaction():
            db_user = await UserService.get_user_by_key(conn, key)
            if not db_user:
                raise NotFoundError(f"User with key {key} not found")
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
                raise NotFoundError(f"User with key {key} not found")
            if not PasswordHasher.verify(
                user.current_password, db_user["hashed_password"]
            ):
                raise ValidationError("Current password is incorrect")
            hashed_password = PasswordHasher.hash(user.password)
            updated_user = await conn.fetchrow(
                """
                UPDATE users
                SET hashed_password = $1
                WHERE key = $2
                RETURNING *
                """,
                hashed_password,
                key,
            )
            return updated_user
