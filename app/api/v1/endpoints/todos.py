# app/api/v1/endpoints/todos.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.todo_service import TodoService
from app.database import get_db
from sqlalchemy.orm import Session
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse, TodoListResponse
from app.schemas.user import User
from app.api import get_current_user
from app.schemas.user import User as UserSchema
from typing import Annotated

router = APIRouter(dependencies=[Depends(get_current_user)])

# Schema for partial priority update


@router.get("/")
def get_todos(
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Session = Depends(get_db), 
    page: int = 1, 
    size: int = 10
):
    skip = (page - 1) * size
    todos = TodoService.get_todos(db, current_user.key, skip, size)
    total = TodoService.get_total_todos(db)
    return TodoListResponse(
        todos=[TodoResponse(**todo.to_dict()) for todo in todos],
        total=total,
        page=page,
        size=len(todos),
        success=True,
    )


@router.get("/{key}")
def get_todo_by_key(
    key: str, 
    current_user: Annotated[UserSchema, Depends(get_current_user)], 
    db: Session = Depends(get_db)
):
    try:
        todo_id = TodoService.fetch_todo_id_by_key(db, key, current_user.key)
        todo = TodoService.get_todo(db, todo_id, current_user.key)
        return TodoResponse(**todo.to_dict())
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Todo with key {key} not found")


@router.post("/")
def create_todo(
    todo: TodoCreate, 
    current_user: Annotated[UserSchema, Depends(get_current_user)], 
    db: Session = Depends(get_db)
):
    try:
        todo = TodoService.create_todo(db, todo, current_user.key)
        return TodoResponse(**todo.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{key}")
def update_todo(
    key: str, 
    todo: TodoUpdate, 
    current_user: Annotated[UserSchema, Depends(get_current_user)], 
    db: Session = Depends(get_db)
):
    try:
        todo_id = TodoService.fetch_todo_id_by_key(db, key, current_user.key)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Todo with key {key} not found")

    try:
        todo = TodoService.update_todo(db, todo_id, todo, current_user.key)
        return TodoResponse(**todo.to_dict())
    except Exception:
        raise HTTPException(
            status_code=500, detail="Internal server error while updating todo"
        )


@router.patch("/{key}")
def patch_todo(
    key: str, 
    todo_patch: dict, 
    current_user: Annotated[UserSchema, Depends(get_current_user)], 
    db: Session = Depends(get_db)
):
    try:
        todo_id = TodoService.fetch_todo_id_by_key(db, key, current_user.key)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Todo with key {key} not found")

    try:
        # Only update fields that are provided
        updated_todo = TodoService.patch_todo(db, todo_id, todo_patch, current_user.key)
        return TodoResponse(**updated_todo.to_dict())
    except Exception:
        raise HTTPException(
            status_code=500, detail="Internal server error while updating todo"
        )


@router.delete("/{key}")
def delete_todo(
    key: str, 
    current_user: Annotated[UserSchema, Depends(get_current_user)], 
    db: Session = Depends(get_db)
):
    try:
        todo_id = TodoService.fetch_todo_id_by_key(db, key, current_user.key)
        if TodoService.delete_todo(db, todo_id, current_user.key):
            return {"message": "Todo deleted successfully"}
        else:
            raise HTTPException(
                status_code=500, detail="Internal server error while deleting todo"
            )
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Todo with key {key} not found")
