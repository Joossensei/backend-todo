from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate, UserUpdate, UserUpdatePassword
import uuid
from app.api import get_current_user
from app.core.security import PasswordHasher
from app.core.rate_limit import limiter
from slowapi.util import get_remote_address

router = APIRouter()


@router.get("/", response_model=List[User], dependencies=[Depends(get_current_user)])
@limiter.limit("10/second;200/minute")
def read_users(request: Request, response: Response, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        users = db.query(UserModel).offset(skip).limit(limit).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error while getting users (original error message: {e})")


@router.get("/{key}", response_model=User, dependencies=[Depends(get_current_user)])
@limiter.limit("20/second;400/minute")
def read_user(request: Request, response: Response, key: str, db: Session = Depends(get_db)):
    try:
        user = db.query(UserModel).filter(UserModel.key == key).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error while getting user (original error message: {e})")


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute;50/hour", key_func=get_remote_address)
def create_user(request: Request, response: Response, user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        # Ensure username is unique
        existing_user = db.query(UserModel).filter(UserModel.username == user_in.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        # Generate a UUID for the key
        user_key = str(uuid.uuid4())
        db_user = UserModel(
            key=user_key,
            name=user_in.name,
            username=user_in.username,
            email=user_in.email,
            hashed_password=PasswordHasher.hash(user_in.password),
            is_active=user_in.is_active,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error while creating user (original error message: {e})")


@router.put("/{key}", response_model=User, dependencies=[Depends(get_current_user)])
@limiter.limit("10/minute;100/hour")
def update_user(request: Request, response: Response, key: str, user_in: UserUpdate, db: Session = Depends(get_db)):
    try:
        user = db.query(UserModel).filter(UserModel.key == key).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user_in.name is not None:
            user.name = user_in.name
        if user_in.email is not None:
            user.email = user_in.email
        if user_in.is_active is not None:
            user.is_active = user_in.is_active
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error while updating user (original error message: {e})")


@router.put("/{key}/password", response_model=User, dependencies=[Depends(get_current_user)])
@limiter.limit("10/minute;100/hour")
def update_user_password(request: Request, response: Response, key: str, user_in: UserUpdatePassword, db: Session = Depends(get_db)):
    try:
        user = db.query(UserModel).filter(UserModel.key == key).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not PasswordHasher.verify(user_in.current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid current password")
        user.hashed_password = PasswordHasher.hash(user_in.password)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error while updating user password (original error message: {e})")


@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
@limiter.limit("10/minute;50/hour")
def delete_user(request: Request, response: Response, key: str, db: Session = Depends(get_db)):
    try:
        user = db.query(UserModel).filter(UserModel.key == key).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error while deleting user (original error message: {e})")
