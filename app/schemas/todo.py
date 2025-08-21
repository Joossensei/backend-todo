# app/schemas/todo.py
from pydantic import BaseModel, Field, model_serializer
from typing import Optional
from datetime import datetime


class TodoCreate(BaseModel):
    title: str = Field(...)
    description: Optional[str] = None
    priority: str = Field(...)
    completed: Optional[bool] = None
    user_key: str
    status: str = Field(...)


class TodoUpdate(BaseModel):
    title: str = Field(...)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: str = Field(...)
    status: str = Field(...)


class TodoPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class TodoResponse(BaseModel):
    key: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    user_key: str
    status: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    @model_serializer
    def ser_model(self) -> dict:
        return {
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "priority": self.priority,
            "status": self.status if self.status else None,
            "user_key": self.user_key,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TodoListResponse(BaseModel):
    todos: list[TodoResponse]
    total: int
    page: int
    size: int
    success: bool
    next_link: Optional[str] = None
    prev_link: Optional[str] = None
