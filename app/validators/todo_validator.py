from app.core.errors import NotFoundError, ValidationError
from app.schemas.todo import TodoCreate, TodoUpdate, TodoPatch
from app.services.priority_service import PriorityService
import asyncpg
import logging

logger = logging.getLogger(__name__)


class TodoCreateValidator:
    def validate_todo_title(
        todo: TodoCreate,
    ) -> TodoCreate:
        if todo.title.strip() == "":
            raise ValidationError("Title is required")
        if len(todo.title) > 100:
            raise ValidationError("Title must be less than 100 characters")

    async def validate_todo_priority(
        todo: TodoCreate,
        db: asyncpg.Connection,
        user_key: str,
    ) -> TodoCreate:
        if todo.priority.strip() == "":
            raise ValidationError("Priority is required")
        if len(todo.priority) > 36:
            raise ValidationError("Priority must be less than 36 characters")
        try:
            await PriorityService.fetch_priority_id_by_key(db, todo.priority, user_key)
        except NotFoundError:
            raise ValidationError("Priority not found")
        return todo

    def validate_todo_description(
        todo: TodoCreate,
    ) -> TodoCreate:
        if todo.description is not None:
            if len(todo.description) > 1000:
                raise ValidationError("Description must be less than 1000 characters")
        return todo

    def validate_todo_completed(
        todo: TodoCreate,
    ) -> TodoCreate:
        if todo.completed is None:
            raise ValidationError("Completed is required")
        if todo.completed is not None and todo.completed not in [True, False]:
            raise ValidationError("Completed must be a boolean")
        return todo

    def validate_todo_user_key(
        todo: TodoCreate,
        user_key: str,
    ) -> TodoCreate:
        if todo.user_key != user_key:
            raise ValidationError("User key is not valid")
        return todo

    async def validate_todo(
        todo: TodoCreate, db: asyncpg.Connection, user_key: str
    ) -> TodoCreate:
        TodoCreateValidator.validate_todo_title(todo)
        await TodoCreateValidator.validate_todo_priority(todo, db, user_key)
        TodoCreateValidator.validate_todo_description(todo)
        TodoCreateValidator.validate_todo_completed(todo)
        TodoCreateValidator.validate_todo_user_key(todo, user_key)
        return todo


class TodoUpdateValidator:
    def validate_todo_title(
        todo: TodoUpdate,
    ) -> TodoUpdate:
        if todo.title.strip() == "":
            raise ValidationError("Title is required")
        if len(todo.title) > 100:
            raise ValidationError("Title must be less than 100 characters")
        return todo

    def validate_todo_description(
        todo: TodoUpdate,
    ) -> TodoUpdate:
        if todo.description is not None:
            if len(todo.description) > 1000:
                raise ValidationError("Description must be less than 1000 characters")
        return todo

    def validate_todo_completed(
        todo: TodoUpdate,
    ) -> TodoUpdate:
        if todo.completed is not None:
            if todo.completed not in [True, False]:
                raise ValidationError("Completed must be a boolean")
        return todo

    async def validate_todo_priority(
        todo: TodoUpdate,
        db: asyncpg.Connection,
        user_key: str,
    ) -> TodoUpdate:
        if todo.priority.strip() == "":
            raise ValidationError("Priority is required")
        if len(todo.priority) > 36:
            raise ValidationError("Priority must be less than 36 characters")
        try:
            await PriorityService.fetch_priority_id_by_key(db, todo.priority, user_key)
        except NotFoundError:
            raise ValidationError("Priority not found")
        return todo

    async def validate_todo(
        todo: TodoUpdate, db: asyncpg.Connection, user_key: str
    ) -> TodoUpdate:
        TodoUpdateValidator.validate_todo_title(todo)
        TodoUpdateValidator.validate_todo_description(todo)
        TodoUpdateValidator.validate_todo_completed(todo)
        await TodoUpdateValidator.validate_todo_priority(todo, db, user_key)
        return todo


class TodoPatchValidator:
    def validate_todo_title(
        todo: TodoPatch,
    ) -> TodoPatch:
        if todo.title is not None:
            if todo.title.strip() == "":
                raise ValidationError("Title is required")
            if len(todo.title) > 100:
                raise ValidationError("Title must be less than 100 characters")

    def validate_todo_description(
        todo: TodoPatch,
    ) -> TodoPatch:
        if todo.description is not None:
            if len(todo.description) > 1000:
                raise ValidationError("Description must be less than 1000 characters")
        return todo

    def validate_todo_completed(
        todo: TodoPatch,
    ) -> TodoPatch:
        if todo.completed is not None:
            if todo.completed not in [True, False]:
                raise ValidationError("Completed must be a boolean")
        return todo

    async def validate_todo_priority(
        todo: TodoPatch,
        db: asyncpg.Connection,
        user_key: str,
    ) -> TodoPatch:
        if todo.priority is not None:
            if todo.priority.strip() == "":
                raise ValidationError("Priority is required")
            if len(todo.priority) > 36:
                raise ValidationError("Priority must be less than 36 characters")
            try:
                await PriorityService.fetch_priority_id_by_key(
                    db, todo.priority, user_key
                )
            except NotFoundError:
                raise ValidationError("Priority not found")
            return todo

    async def validate_todo(
        todo: TodoPatch, db: asyncpg.Connection, user_key: str
    ) -> TodoPatch:
        TodoPatchValidator.validate_todo_title(todo)
        TodoPatchValidator.validate_todo_description(todo)
        TodoPatchValidator.validate_todo_completed(todo)
        await TodoPatchValidator.validate_todo_priority(todo, db, user_key)
        return todo
