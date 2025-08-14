from app.models.user import User as UserModel
from app.core.security import PasswordHasher
from app.schemas.user import UserCreate, UserUpdate, UserUpdatePassword
from sqlalchemy.orm import Session
import uuid


class UserService:
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 10):
        return db.query(UserModel).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_by_key(db: Session, key: str):
        return db.query(UserModel).filter(UserModel.key == key).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(UserModel).filter(UserModel.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(UserModel).filter(UserModel.username == username).first()

    @staticmethod
    def create_user(db: Session, user: UserCreate):
        if UserService.get_user_by_username(db, user.username):
            raise ValueError(f"User with username {user.username} already exists")
        if UserService.get_user_by_email(db, user.email):
            raise ValueError(f"User with email {user.email} already exists")
        db_user = UserModel(
            key=str(uuid.uuid4()),
            name=user.name,
            username=user.username,
            email=user.email,
            hashed_password=PasswordHasher.hash(user.password),
            is_active=user.is_active,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(db: Session, key: str, user: UserUpdate):
        db_user = UserService.get_user_by_key(db, key)
        if not db_user:
            raise ValueError(f"User with key {key} not found")
        if user.name is not None:
            db_user.name = user.name
        if user.email is not None:
            db_user.email = user.email
        if user.is_active is not None:
            db_user.is_active = user.is_active
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, key: str):
        db_user = UserService.get_user_by_key(db, key)
        if not db_user:
            raise ValueError(f"User with key {key} not found")
        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    def get_total_users(db: Session):
        return db.query(UserModel).count()

    @staticmethod
    def update_user_password(db: Session, key: str, user: UserUpdatePassword):
        db_user = UserService.get_user_by_key(db, key)
        if not db_user:
            raise ValueError(f"User with key {key} not found")
        if not PasswordHasher.verify(user.current_password, db_user.hashed_password):
            raise ValueError("Current password is incorrect")
        db_user.hashed_password = PasswordHasher.hash(user.password)
        db.commit()
        db.refresh(db_user)
        return db_user
