# app/services/auth_service.py
import asyncpg
from app.core.security import TokenManager
from app.core.config import settings
from datetime import timedelta


class AuthService:
    @staticmethod
    async def authenticate(
        connection: asyncpg.Connection, username: str, password: str
    ) -> str:
        """Authenticate user and return access token."""
        # Get user by username
        user_data = await connection.fetchrow(
            "SELECT * FROM users WHERE username = $1", username
        )

        if not user_data:
            return None

        # Verify password
        if not TokenManager.verify_password(password, user_data["hashed_password"]):
            return None

        # Create access token
        access_token_expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        access_token = TokenManager.create_access_token(
            data={"sub": user_data["username"]}, expires_delta=access_token_expires
        )

        return access_token
