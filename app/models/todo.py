# app/models/todo.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.sql import func
from db.database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(36), unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String(36), ForeignKey("priorities.key"), nullable=False)
    user_key = Column(String(36), ForeignKey("users.key"), nullable=False)
    status = Column(String(36), ForeignKey("statuses.key"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Index for user_key
    __table_args__ = (
        Index("ix_todo_user_key", "user_key"),
        Index("ix_todo_priority", "priority"),
        Index("ix_todo_completed", "completed"),
        Index("ix_todo_user_key_key", "user_key", "key"),
        Index("ix_todo_user_key_completed", "user_key", "completed"),
        Index("ix_todo_user_key_priority", "user_key", "priority"),
        Index("ix_todo_user_key_status", "user_key", "status"),
    )

    def __str__(self):
        return (
            f"Todo(id={self.id}, title='{self.title}',"
            f" key='{self.key}', completed={self.completed}, user_key={self.user_key},"
            f" status={self.status})"
        )

    def __repr__(self):
        return (
            f"<Todo(id={self.id}, title='{self.title}',"
            f" key='{self.key}', completed={self.completed},"
            f" priority={self.priority}, user_key={self.user_key},"
            f" status={self.status})>"
        )

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "priority": self.priority,
            "user_key": self.user_key,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def pretty_print(self):
        """Pretty print the todo object"""
        print(f"📝 Todo: {self.title}")
        print(f"   ID: {self.id}")
        print(f"   Key: {self.key}")
        print(f"   Completed: {self.completed}")
        print(f"   Priority: {self.priority}")
        print(f"   User Key: {self.user_key}")
        print(f"   Status: {self.status}")
        if self.description:
            print(f"   Description: {self.description}")
        print(f"   Created: {self.created_at}")
        print(f"   Updated: {self.updated_at}")
