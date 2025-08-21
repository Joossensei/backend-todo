from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from db.database import Base


class Status(Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(36), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    user_key = Column(String(36), nullable=False)
    order = Column(Integer, nullable=False)
    color = Column(String(36), nullable=False)
    icon = Column(String(36), nullable=False)
    is_default = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Status {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "user_key": self.user_key,
            "order": self.order,
            "color": self.color,
            "icon": self.icon,
            "is_default": self.is_default,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def pretty_print(self):
        print(self.to_dict())
