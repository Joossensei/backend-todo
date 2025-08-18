from pydantic import BaseModel, EmailStr, ConfigDict, model_serializer
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    name: str
    username: str
    email: EmailStr
    is_active: bool = True


class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str
    is_active: bool = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserUpdatePassword(BaseModel):
    current_password: str
    password: str


class UserInDBBase(UserBase):
    id: int
    key: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: int
    key: str
    name: str
    username: str
    email: EmailStr
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserInDBBase):
    hashed_password: str


class UserResponse(BaseModel):
    key: str
    name: str
    username: str
    email: EmailStr
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_serializer
    def ser_model(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    size: int
    success: bool
    next_link: Optional[str] = None
    prev_link: Optional[str] = None
