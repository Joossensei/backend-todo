from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.sql import func
from db.database import Base


class Priority(Base):
    __tablename__ = "priorities"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(36), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(100), nullable=False)
    icon = Column(String(100), nullable=True)  # Icon identifier for frontend
    order = Column(Integer, nullable=False)
    user_key = Column(String(36), ForeignKey("users.key"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Index and constraints for user_key
    __table_args__ = (
        UniqueConstraint("user_key", "name", name="uq_priority_user_name"),
        UniqueConstraint("user_key", "order", name="uq_priority_user_order"),
        Index("ix_priority_user_key", "user_key"),
        Index("ix_priority_user_key_key", "user_key", "key"),
    )

    def __str__(self):
        return (
            f"Priority(id={self.id}, name='{self.name}',"
            f" key='{self.key}', color='{self.color}', icon='{self.icon}',"
            f" order={self.order}, user_key={self.user_key})"
        )

    def __repr__(self):
        return (
            f"<Priority(id={self.id}, name='{self.name}',"
            f" key='{self.key}', color='{self.color}', icon='{self.icon}',"
            f" order={self.order}, user_key={self.user_key})>"
        )

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
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

    def pretty_print(self):
        """Pretty print the priority object"""
        print(f"🎯 Priority: {self.name}")
        print(f"   ID: {self.id}")
        print(f"   Key: {self.key}")
        print(f"   Color: {self.color}")
        print(f"   Icon: {self.icon}")
        print(f"   Order: {self.order}")
        print(f"   User Key: {self.user_key}")
        if self.description:
            print(f"   Description: {self.description}")
        print(f"   Created: {self.created_at}")
        print(f"   Updated: {self.updated_at}")
