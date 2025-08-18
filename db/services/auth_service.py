from datetime import datetime, timedelta, timezone
from app.core.security import PasswordHasher, TokenManager
import asyncpg


class AuthService:
    @staticmethod
    async def get_user(conn: asyncpg.Connection, username: str):
        user = await conn.fetchrow("SELECT * FROM users WHERE username = $1", username)
        return user

    async def authenticate_user(conn: asyncpg.Connection, username: str, password: str):
        user = await AuthService.get_user(conn, username)
        if not user:
            return False
        if not PasswordHasher.verify(password, user["hashed_password"]):
            return False
        return user

    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = TokenManager.encode(to_encode)
        return encoded_jwt
