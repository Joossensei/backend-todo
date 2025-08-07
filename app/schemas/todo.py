# app/schemas/todo.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Request schemas (what your API accepts)
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    priority: int = Field(1, ge=1, le=5)
    completed: bool = False

class TodoUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    completed: bool = False
    priority: int = Field(1, ge=1, le=5)

# Response schemas (what your API returns)
class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: int
    created_at: datetime
    updated_at: Optional[datetime]

# List response schema
class TodoListResponse(BaseModel):
    todos: list[TodoResponse]
    total: int
    page: int
    size: int