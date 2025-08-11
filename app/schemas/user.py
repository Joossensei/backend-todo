from pydantic import BaseModel, EmailStr
from typing import Optional
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

    class Config:
        from_attributes = True


class User(BaseModel):
    id: int
    key: str
    name: str
    username: str
    email: EmailStr
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInDB(UserInDBBase):
    hashed_password: str
