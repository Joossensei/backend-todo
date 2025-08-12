# app/services/priority_service.py
from sqlalchemy.orm import Session
from app.models.priority import Priority
from app.schemas.priority import PriorityCreate, PriorityUpdate
import uuid


class PriorityService:
    @staticmethod
    def create_priority(
        db: Session, priority: PriorityCreate, user_key: str
    ) -> Priority:
        db_priority = Priority(
            key=str(uuid.uuid4()),
            name=priority.name,
            description=priority.description,
            color=priority.color,
            icon=priority.icon,
            order=priority.order,
            user_key=user_key,
        )
        db.add(db_priority)
        db.commit()
        db.refresh(db_priority)
        return db_priority

    @staticmethod
    def fetch_priority_id_by_key(db: Session, key: str, user_key: str) -> int:
        """Get a priority by its UUID key instead of ID."""
        db_priorities = db.query(Priority).filter(
            Priority.key == key, Priority.user_key == user_key
        )
        if db_priorities.count() == 0:
            raise ValueError(f"Priority with key {key} not found")
        if db_priorities.count() > 1:
            raise ValueError(f"Multiple priorities found with key {key}")
        return db_priorities.first().id

    @staticmethod
    def get_priorities(db: Session, user_key: str, skip: int = 0, limit: int = 10):
        return (
            db.query(Priority)
            .filter(Priority.user_key == user_key)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_priority(db: Session, priority_id: int, user_key: str):
        return (
            db.query(Priority)
            .filter(Priority.id == priority_id, Priority.user_key == user_key)
            .first()
        )

    @staticmethod
    def update_priority(
        db: Session, priority_id: int, priority_update: PriorityUpdate, user_key: str
    ) -> Priority:
        db_priority = (
            db.query(Priority)
            .filter(Priority.id == priority_id, Priority.user_key == user_key)
            .first()
        )
        if db_priority:
            for field, value in priority_update.model_dump(exclude_unset=True).items():
                setattr(db_priority, field, value)
            db.commit()
            db.refresh(db_priority)
        return db_priority

    @staticmethod
    def delete_priority(db: Session, priority_id: int, user_key: str) -> bool:
        db_priority = (
            db.query(Priority)
            .filter(Priority.id == priority_id, Priority.user_key == user_key)
            .first()
        )

        if not db_priority:
            raise ValueError(f"Priority with id {priority_id} not found")

        db.delete(db_priority)
        db.commit()
        return True  # Successfully deleted

    @staticmethod
    def get_total_priorities(db: Session, user_key: str) -> int:
        return db.query(Priority).filter(Priority.user_key == user_key).count()

    @staticmethod
    def patch_priority(
        db: Session, priority_id: int, priority_patch: dict, user_key: str
    ) -> Priority:
        db_priority = (
            db.query(Priority)
            .filter(Priority.id == priority_id, Priority.user_key == user_key)
            .first()
        )
        if not db_priority:
            raise ValueError(f"Priority with id {priority_id} not found")

        for field, value in priority_patch.items():
            setattr(db_priority, field, value)
        db.commit()
        db.refresh(db_priority)
        return db_priority

    @staticmethod
    def check_availability(
        db: Session, priority: PriorityCreate, user_key: str
    ) -> tuple[bool, str]:
        # Make sure the name is not already taken
        db_priority = (
            db.query(Priority)
            .filter(Priority.name == priority.name, Priority.user_key == user_key)
            .first()
        )
        if db_priority:
            return False, "Name already taken"
        # Make sure the order is not already taken
        db_priority = (
            db.query(Priority)
            .filter(Priority.order == priority.order, Priority.user_key == user_key)
            .first()
        )
        if db_priority:
            return False, "Order already taken"
        return True, "Available"
