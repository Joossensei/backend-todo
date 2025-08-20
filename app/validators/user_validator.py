from app.schemas.user import UserCreate, UserUpdate, UserUpdatePassword
from app.core.errors import ValidationError, NotFoundError
from app.services.user_service import UserService
import asyncpg
import re
import logging
from app.core.security import PasswordHasher

logger = logging.getLogger(__name__)


class UserCreateValidator:
    def validate_user_name(
        user: UserCreate,
    ) -> UserCreate:
        if user.name.strip() == "":
            raise ValidationError("Name is required")
        if len(user.name) > 100:
            raise ValidationError("Name must be less than 100 characters")
        return user

    def validate_user_username(
        user: UserCreate,
    ) -> UserCreate:
        if user.username.strip() == "":
            raise ValidationError("Username is required")
        if len(user.username) > 50:
            raise ValidationError("Username must be less than 50 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", user.username):
            raise ValidationError(
                "Username can only contain letters, numbers, and underscores"
            )
        return user

    def validate_user_email(
        user: UserCreate,
    ) -> UserCreate:
        if user.email.strip() == "":
            raise ValidationError("Email is required")
        if len(user.email) > 255:
            raise ValidationError("Email must be less than 255 characters")
        # EmailStr from pydantic already validates email format
        return user

    def validate_user_password(
        user: UserCreate,
    ) -> UserCreate:
        if user.password.strip() == "":
            raise ValidationError("Password is required")
        if len(user.password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if len(user.password) > 128:
            raise ValidationError("Password must be less than 128 characters")
        if not re.search(r"[A-Z]", user.password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", user.password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", user.password):
            raise ValidationError("Password must contain at least one number")
        return user

    def validate_user_is_active(
        user: UserCreate,
    ) -> UserCreate:
        if not isinstance(user.is_active, bool):
            raise ValidationError("Is active must be a boolean")
        return user

    async def validate_user_username_unique(
        user: UserCreate,
        db: asyncpg.Connection,
    ) -> UserCreate:
        existing_user = await UserService.get_user_by_username(db, user.username)
        if existing_user:
            raise ValidationError("Username already exists")
        return user

    async def validate_user_email_unique(
        user: UserCreate,
        db: asyncpg.Connection,
    ) -> UserCreate:
        existing_user = await UserService.get_user_by_email(db, user.email)
        if existing_user:
            raise ValidationError("Email already exists")
        return user

    async def validate_user(user: UserCreate, db: asyncpg.Connection) -> UserCreate:
        UserCreateValidator.validate_user_name(user)
        UserCreateValidator.validate_user_username(user)
        UserCreateValidator.validate_user_email(user)
        UserCreateValidator.validate_user_password(user)
        UserCreateValidator.validate_user_is_active(user)
        await UserCreateValidator.validate_user_username_unique(user, db)
        await UserCreateValidator.validate_user_email_unique(user, db)
        return user


class UserUpdateValidator:
    def validate_user_name(
        user: UserUpdate,
    ) -> UserUpdate:
        if user.name is not None:
            if user.name.strip() == "":
                raise ValidationError("Name is required")
            if len(user.name) > 100:
                raise ValidationError("Name must be less than 100 characters")
        return user

    def validate_user_email(
        user: UserUpdate,
    ) -> UserUpdate:
        if user.email is not None:
            if user.email.strip() == "":
                raise ValidationError("Email is required")
            if len(user.email) > 255:
                raise ValidationError("Email must be less than 255 characters")
            # EmailStr from pydantic already validates email format
        return user

    def validate_user_is_active(
        user: UserUpdate,
    ) -> UserUpdate:
        if user.is_active is not None:
            if not isinstance(user.is_active, bool):
                raise ValidationError("Is active must be a boolean")
        return user

    async def validate_user_email_unique(
        user: UserUpdate,
        db: asyncpg.Connection,
        current_user_key: str,
    ) -> UserUpdate:
        if user.email is not None:
            existing_user = await UserService.get_user_by_email(db, user.email)
            if existing_user and existing_user.key != current_user_key:
                raise ValidationError("Email already exists")
        return user

    async def validate_user(
        user: UserUpdate, db: asyncpg.Connection, current_user_key: str
    ) -> UserUpdate:
        try:
            UserUpdateValidator.validate_user_name(user)
            UserUpdateValidator.validate_user_email(user)
            UserUpdateValidator.validate_user_is_active(user)
            await UserUpdateValidator.validate_user_email_unique(
                user, db, current_user_key
            )
            return user
        except ValidationError as e:
            raise ValidationError(custom_message=str(e))


class UserUpdatePasswordValidator:
    def validate_current_password(
        user: UserUpdatePassword,
    ) -> UserUpdatePassword:
        if user.current_password.strip() == "":
            raise ValidationError("Current password is required")
        return user

    def validate_new_password(
        user: UserUpdatePassword,
    ) -> UserUpdatePassword:
        if user.password.strip() == "":
            raise ValidationError("New password is required")
        if len(user.password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if len(user.password) > 128:
            raise ValidationError("Password must be less than 128 characters")
        # Check for at least one uppercase letter, one lowercase letter, and one number
        if not re.search(r"[A-Z]", user.password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", user.password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", user.password):
            raise ValidationError("Password must contain at least one number")
        return user

    def validate_passwords_different(
        user: UserUpdatePassword,
    ) -> UserUpdatePassword:
        if user.current_password == user.password:
            raise ValidationError(
                "New password must be different from current password"
            )
        return user

    async def validate_current_password_correct(
        user: UserUpdatePassword,
        db: asyncpg.Connection,
        user_key: str,
    ) -> UserUpdatePassword:
        db_user = await UserService.get_user_by_key(db, user_key)
        if not db_user:
            raise NotFoundError(f"User with key {user_key} not found")
        if not PasswordHasher.verify(user.current_password, db_user["hashed_password"]):
            raise ValidationError("Current password is incorrect")
        return user

    async def validate_user_password(
        user: UserUpdatePassword, db: asyncpg.Connection, user_key: str
    ) -> UserUpdatePassword:
        UserUpdatePasswordValidator.validate_current_password(user)
        UserUpdatePasswordValidator.validate_new_password(user)
        UserUpdatePasswordValidator.validate_passwords_different(user)
        await UserUpdatePasswordValidator.validate_current_password_correct(
            user, db, user_key
        )
        return user
