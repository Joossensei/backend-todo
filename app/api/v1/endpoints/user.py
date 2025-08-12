from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserUpdatePassword,
    UserListResponse,
    UserResponse,
)
from app.api import get_current_user
from app.core.rate_limit import limiter
from slowapi.util import get_remote_address
from app.services import UserService

router = APIRouter()


@router.get(
    "/", response_model=UserListResponse, dependencies=[Depends(get_current_user)]
)
@limiter.limit("10/second;200/minute")
def read_users(
    request: Request,
    response: Response,
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db),
):
    if size > 100:
        raise HTTPException(status_code=400, detail="Size cannot be greater than 100")
    if page < 1:
        raise HTTPException(status_code=400, detail="Page cannot be less than 1")
    try:
        skip = (page - 1) * size
        users = UserService.get_users(db, skip, size)
        total = UserService.get_total_users(db)
        return UserListResponse(
            users=[UserResponse(**user.model_dump()) for user in users],
            total=total,
            page=page,
            size=len(users),
            success=True,
            next_link=(
                f"/users?page={page + 1}&size={size}" if page * size < total else None
            ),
            prev_link=(f"/users?page={page - 1}&size={size}" if page > 1 else None),
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while getting users (original error message: {e})",
        )


@router.get(
    "/{key}", response_model=UserResponse, dependencies=[Depends(get_current_user)]
)
@limiter.limit("20/second;400/minute")
def read_user(
    request: Request, response: Response, key: str, db: Session = Depends(get_db)
):
    try:
        user = UserService.get_user_by_key(db, key)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**user.model_dump())
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while getting user (original error message: {e})",
        )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute;50/hour", key_func=get_remote_address)
def create_user(
    request: Request,
    response: Response,
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        # Ensure username is unique
        existing_user = UserService.get_user_by_username(db, user_in.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        db_user = UserService.create_user(db, user_in)
        return UserResponse(**db_user.model_dump())
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while creating user (original error message: {e})",
        )


@router.put(
    "/{key}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
@limiter.limit("10/minute;100/hour")
def update_user(
    request: Request,
    response: Response,
    key: str,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
):
    try:
        # Check if the user is the current user
        current_user = get_current_user(
            request,
            request.headers.get("Authorization").split(" ")[1],
            db,
        )
        if current_user.key != key:
            raise HTTPException(
                status_code=403, detail="You are not allowed to update this user"
            )
        user = UserService.update_user(db, key, user_in)
        return UserResponse(**user.model_dump())
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while updating user (original error message: {e})",
        )


@router.put(
    "/{key}/password",
    dependencies=[Depends(get_current_user)],
)
@limiter.limit("10/minute;100/hour")
def update_user_password(
    request: Request,
    response: Response,
    key: str,
    user_in: UserUpdatePassword,
    db: Session = Depends(get_db),
):
    try:
        # Check if the user is the current user
        current_user = get_current_user(
            request,
            request.headers.get("Authorization").split(" ")[1],
            db,
        )
        if current_user.key != key:
            raise HTTPException(
                status_code=403, detail="You are not allowed to update this user"
            )
        # Update the user password
        UserService.update_user_password(db, key, user_in)
        return {"message": "User password updated successfully"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while updating user password (original error message: {e})",
        )


@router.delete(
    "/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
@limiter.limit("10/minute;50/hour")
def delete_user(
    request: Request, response: Response, key: str, db: Session = Depends(get_db)
):
    try:
        # Check if the user is the current user
        current_user = get_current_user(
            request,
            request.headers.get("Authorization").split(" ")[1],
            db,
        )
        if current_user.key != key:
            raise HTTPException(
                status_code=403, detail="You are not allowed to delete this user"
            )
        # Delete the user
        user = UserService.get_user_by_key(db, key)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while deleting user (original error message: {e})",
        )
