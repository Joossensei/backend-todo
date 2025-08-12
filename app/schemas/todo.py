# app/schemas/todo.py
from pydantic import BaseModel, Field
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


class TodoListResponse(BaseModel):
    todos: list[TodoResponse]
    total: int
    page: int
    size: int
    success: bool
    next_link: Optional[str] = None
    prev_link: Optional[str] = None
