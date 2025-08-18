# app/schemas/todo.py
from pydantic import BaseModel, Field, model_serializer
from typing import Optional
from datetime import datetime


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    priority: str = Field(..., min_length=1, max_length=36)
    completed: bool = False
    user_key: str


class TodoUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    completed: bool = False
    priority: str = Field(..., min_length=1, max_length=36)


class TodoResponse(BaseModel):
    key: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    user_key: str
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
