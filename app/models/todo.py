# app/models/todo.py
from sqlalchemy import (Column, Integer, String, Boolean, DateTime, Text,
                        ForeignKey)
from sqlalchemy.sql import func
from app.database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(36), unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String(36),
                      ForeignKey("priorities.key"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        return f"Todo(id={self.id}, title='{self.title}'," \
            f" key='{self.key}', completed={self.completed})"

    def __repr__(self):
        return f"<Todo(id={self.id}, title='{self.title}'," \
            f" key='{self.key}', completed={self.completed}," \
            f" priority={self.priority})>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'key': self.key,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'priority': self.priority,
            'created_at': self.created_at.isoformat()
            if self.created_at else None,
            'updated_at': self.updated_at.isoformat()
            if self.updated_at else None
        }

    def pretty_print(self):
        """Pretty print the todo object"""
        print(f"📝 Todo: {self.title}")
        print(f"   ID: {self.id}")
        print(f"   Key: {self.key}")
        print(f"   Completed: {self.completed}")
        print(f"   Priority: {self.priority}")
        if self.description:
            print(f"   Description: {self.description}")
        print(f"   Created: {self.created_at}")
        print(f"   Updated: {self.updated_at}")
