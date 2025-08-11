# app/schemas/todo.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Request schemas (what your API accepts)


class PriorityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=100)
    order: int = Field(1, ge=1)
    user_key: str

class PriorityUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=100)
    order: int = Field(1, ge=1)


# Response schemas (what your API returns)
class PriorityResponse(BaseModel):
    key: str
    name: str
    description: Optional[str]
    color: str
    icon: Optional[str]
    order: int
    user_key: str
    created_at: datetime
    updated_at: Optional[datetime]

# List response schema


class PriorityListResponse(BaseModel):
    priorities: list[PriorityResponse]
    total: int
    page: int
    size: int
    success: bool
    next_link: Optional[str] = None
