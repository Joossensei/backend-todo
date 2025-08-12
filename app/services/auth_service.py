from app.models.user import User as UserModel
from datetime import datetime, timedelta, timezone
from app.core.security import PasswordHasher, TokenManager


class AuthService:
    @staticmethod
    def get_user(db, username: str):
        user = db.query(UserModel).filter(UserModel.username == username).first()
        return user

    @staticmethod
    def authenticate_user(db, username: str, password: str):
        user = AuthService.get_user(db, username)
        if not user:
            return False
        if not PasswordHasher.verify(password, user.hashed_password):
            return False
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = TokenManager.encode(to_encode)
        return encoded_jwt
