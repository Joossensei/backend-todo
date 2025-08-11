from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(36), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        return f"User(id={self.id}, name='{self.name}'," \
            f" email='{self.email}', key='{self.key}', is_active={self.is_active})"

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}'," \
            f" email='{self.email}', key='{self.key}', is_active={self.is_active})>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'key': self.key,
            'name': self.name,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

    def pretty_print(self):
        """Pretty print the user"""
        print(self.__str__())