# app/schemas/priority.py
from pydantic import BaseModel, Field, model_serializer
from typing import Optional
from datetime import datetime


class PriorityCreate(BaseModel):
    name: str = Field(...)
    description: Optional[str] = None
    color: str = Field(...)
    icon: str = Field(...)
    order: int = Field(1)
    user_key: str


class PriorityUpdate(BaseModel):
    name: str = Field(...)
    description: Optional[str] = None
    color: str = Field(...)
    icon: Optional[str] = Field(None)
    order: int = Field(1)


class PriorityPatch(BaseModel):
    name: Optional[str] = Field(None)
    description: Optional[str] = None
    color: Optional[str] = Field(None)
    icon: Optional[str] = Field(None)
    order: Optional[int] = Field(None)


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

    @model_serializer
    def ser_model(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "icon": self.icon,
            "order": self.order,
            "user_key": self.user_key,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PriorityListResponse(BaseModel):
    priorities: list[PriorityResponse]
    total: int
    page: int
    size: int
    success: bool
    next_link: Optional[str] = None
    prev_link: Optional[str] = None
