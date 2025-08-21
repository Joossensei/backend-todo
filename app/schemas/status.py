from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_serializer
from typing import List


class Status(BaseModel):
    id: int
    key: str
    name: str
    description: Optional[str] = None
    user_key: str
    order: int
    color: str
    icon: str
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class StatusCreate(BaseModel):
    name: str
    description: Optional[str] = None
    user_key: str
    order: int
    color: str
    icon: str
    is_default: bool


class StatusUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    order: int
    color: str
    icon: str
    is_default: bool


class StatusReorder(BaseModel):
    fromOrder: int = Field(..., description="The current order position")
    toOrder: int = Field(..., description="The target order position")


class StatusPatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_default: Optional[bool] = None


class StatusResponse(BaseModel):
    key: str
    name: str
    description: Optional[str] = None
    user_key: str
    order: int
    color: str
    icon: str
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    @model_serializer
    def ser_model(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "user_key": self.user_key,
            "order": self.order,
            "color": self.color,
            "icon": self.icon,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class StatusListResponse(BaseModel):
    statuses: List[StatusResponse]
    total: int
    page: int
    size: int
    success: bool
    next_link: Optional[str] = None
    prev_link: Optional[str] = None
