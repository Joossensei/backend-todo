import jwt
from app.core.config import settings
from pwdlib import PasswordHash


argon2_hasher = PasswordHash.recommended()


class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        return argon2_hasher.hash(password, salt=bytes(settings.SECRET_KEY, "utf-8"))

    @staticmethod
    def verify(plain: str, hashed: str) -> bool:
        return argon2_hasher.verify(plain, hashed)


class TokenManager:
    @staticmethod
    def encode(payload: dict) -> str:
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode(token: str) -> dict:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    @staticmethod
    def hash_password(password: str) -> str:
        return PasswordHasher.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return PasswordHasher.verify(plain, hashed)

    @staticmethod
    def create_access_token(data: dict, expires_delta=None):
        to_encode = data.copy()
        if expires_delta:
            from datetime import datetime, timedelta, timezone

            expire = datetime.now(timezone.utc) + expires_delta
        else:
            from datetime import datetime, timedelta, timezone

            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = TokenManager.encode(to_encode)
        return encoded_jwt
