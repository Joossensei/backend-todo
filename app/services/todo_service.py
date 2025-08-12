# app/services/todo_service.py
from sqlalchemy.orm import Session
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate
from app.models.priority import Priority
import uuid
from typing import Optional


class TodoService:
    @staticmethod
    def create_todo(db: Session, todo: TodoCreate, user_key: str) -> Todo:
        priority = (
            db.query(Priority)
            .filter(Priority.key == todo.priority, Priority.user_key == user_key)
            .first()
        )
        if not priority:
            raise ValueError(f"Priority with key {todo.priority} not found")
        db_todo = Todo(
            key=str(uuid.uuid4()),
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            priority=priority.key,
            user_key=user_key,
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo

    @staticmethod
    def fetch_todo_id_by_key(db: Session, key: str, user_key: str) -> int:
        """Get a todo by its UUID key instead of ID."""
        db_todos = db.query(Todo).filter(Todo.key == key)
        if db_todos.first().user_key != user_key:
            raise ValueError(f"Todo with key {key} not found for user {user_key}")
        if db_todos.count() == 0:
            raise ValueError(f"Todo with key {key} not found")
        if db_todos.count() > 1:
            raise ValueError(f"Multiple todos found with key {key}")
        return db_todos.first().id

    @staticmethod
    def get_todos(
        db: Session,
        user_key: str,
        skip: int = 0,
        limit: int = 10,
        sort: str = "incomplete-priority-desc",
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
    ):
        query = db.query(Todo).filter(Todo.user_key == user_key)
        if completed is not None:
            query = query.filter(Todo.completed == completed)
        if priority is not None:
            query = query.filter(Todo.priority == priority)
        if search is not None:
            query = query.filter(Todo.title.lower().ilike(f"%{search.lower()}%"))

        if sort == "priority-desc":
            query = query.join(
                Priority,
                (Priority.key == Todo.priority) & (Priority.user_key == user_key),
            ).order_by(Priority.order.asc())
        elif sort == "priority-desc-text-asc":
            query = query.join(
                Priority,
                (Priority.key == Todo.priority) & (Priority.user_key == user_key),
            ).order_by(Priority.order.asc(), Todo.title.asc())
        elif sort == "incomplete-priority-desc":
            query = query.join(
                Priority,
                (Priority.key == Todo.priority) & (Priority.user_key == user_key),
            ).order_by(Todo.completed.asc(), Priority.order.asc())
        elif sort == "text-asc":
            query = query.order_by(Todo.title.asc())
        elif sort == "text-desc":
            query = query.order_by(Todo.title.desc())
        else:
            query = query.order_by(Todo.id.desc())

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_todo(db: Session, todo_id: int, user_key: str):
        return (
            db.query(Todo).filter(Todo.id == todo_id, Todo.user_key == user_key).first()
        )

    @staticmethod
    def update_todo(db: Session, todo_id: int, todo_update: TodoUpdate, user_key: str):
        priority = (
            db.query(Priority).filter(Priority.key == todo_update.priority).first()
        )
        if not priority:
            raise ValueError(f"Priority with id {todo_update.priority} not found")
        todo_update.priority = priority.key
        db_todo = (
            db.query(Todo).filter(Todo.id == todo_id, Todo.user_key == user_key).first()
        )
        if db_todo:
            for field, value in todo_update.model_dump(exclude_unset=True).items():
                if field == "priority":
                    setattr(db_todo, field, priority.key)
                else:
                    setattr(db_todo, field, value)
            db.commit()
            db.refresh(db_todo)
        return db_todo

    @staticmethod
    def delete_todo(db: Session, todo_id: int, user_key: str) -> bool:
        db_todo = (
            db.query(Todo).filter(Todo.id == todo_id, Todo.user_key == user_key).first()
        )

        if not db_todo:
            raise ValueError(f"Todo with id {todo_id} not found")

        db.delete(db_todo)
        db.commit()
        return True  # Successfully deleted

    @staticmethod
    def get_total_todos(db: Session, user_key: str) -> int:
        return db.query(Todo).filter(Todo.user_key == user_key).count()

    @staticmethod
    def patch_todo(db: Session, todo_id: int, todo_patch: dict, user_key: str) -> Todo:
        if "priority" in todo_patch:
            priority = (
                db.query(Priority)
                .filter(Priority.key == todo_patch["priority"])
                .first()
            )
            if not priority:
                raise ValueError(f"Priority with id {todo_patch['priority']} not found")
            todo_patch["priority"] = priority.key
        db_todo = (
            db.query(Todo).filter(Todo.id == todo_id, Todo.user_key == user_key).first()
        )
        if not db_todo:
            raise ValueError(f"Todo with id {todo_id} not found")

        for field, value in todo_patch.items():
            if field == "priority":
                setattr(db_todo, field, priority.key)
            else:
                setattr(db_todo, field, value)
        db.commit()
        db.refresh(db_todo)
        return db_todo
