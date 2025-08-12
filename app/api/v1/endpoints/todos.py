# app/api/v1/endpoints/todos.py
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from app.services.todo_service import TodoService
from app.database import get_db
from sqlalchemy.orm import Session
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse, TodoListResponse
from app.api import get_current_user
from app.schemas.user import User as UserSchema
from typing import Annotated, Optional
from app.core.rate_limit import limiter

router = APIRouter(dependencies=[Depends(get_current_user)])

# Schema for partial priority update

# Query Parameters
# - page: int
# - size: int
# - sort: str (possible values: priority-desc, priority-desc-text-asc, incomplete-priority-desc, text-asc and text-desc)
# - completed: bool (possible values: true, false)
# - priority: str (possible values: priority key)
# - search: str


@router.get("/")
@limiter.limit("10/second;200/minute")
def get_todos(
    request: Request,
    response: Response,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 10,
    sort: str = "incomplete-priority-desc",
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
):
    if size > 100:
        raise HTTPException(status_code=400, detail="Size cannot be greater than 100")
    try:
        skip = (page - 1) * size
        todos = TodoService.get_todos(
            db, current_user.key, skip, size, sort, completed, priority, search
        )
        total = TodoService.get_total_todos(db, current_user.key)
        return TodoListResponse(
            todos=[TodoResponse(**todo.to_dict()) for todo in todos],
            total=total,
            page=page,
            size=len(todos),
            success=True,
            next_link=(
                f"/todos?page={page + 1}&size={size}" if page * size < total else None
            ),
            prev_link=(f"/todos?page={page - 1}&size={size}" if page > 1 else None),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while getting todos (original error message: {e})",
        )


@router.get("/{key}")
@limiter.limit("20/second;400/minute")
def get_todo_by_key(
    request: Request,
    response: Response,
    key: str,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        todo_id = TodoService.fetch_todo_id_by_key(db, key, current_user.key)
        todo = TodoService.get_todo(db, todo_id, current_user.key)
        return TodoResponse(**todo.to_dict())
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Todo with key {key} not found")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while getting todo by key (original error message: {e})",
        )


@router.post("/")
@limiter.limit("10/minute;100/hour")
def create_todo(
    request: Request,
    response: Response,
    todo: TodoCreate,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        todo = TodoService.create_todo(db, todo, current_user.key)
        return TodoResponse(**todo.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while creating todo (original error message: {e})",
        )


@router.put("/{key}")
@limiter.limit("20/minute;200/hour")
def update_todo(
    request: Request,
    response: Response,
    key: str,
    todo: TodoUpdate,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        todo_id = TodoService.fetch_todo_id_by_key(db, key, current_user.key)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Todo with key {key} not found")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while updating todo (original error message: {e})",
        )

    try:
        todo = TodoService.update_todo(db, todo_id, todo, current_user.key)
        return TodoResponse(**todo.to_dict())
    except Exception:
        raise HTTPException(
            status_code=500, detail="Internal server error while updating todo"
        )


@router.patch("/{key}")
@limiter.limit("20/minute;200/hour")
def patch_todo(
    request: Request,
    response: Response,
    key: str,
    todo_patch: dict,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        todo_id = TodoService.fetch_todo_id_by_key(db, key, current_user.key)
    except ValueError as e:
        if current_user.key in str(e):
            raise HTTPException(
                status_code=404,
                detail=f"Todo with key {key} not found for user {current_user.key}",
            )
        else:
            raise HTTPException(status_code=404, detail="Todo not found")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while patching todo (original error message: {e})",
        )

    try:
        # Only update fields that are provided
        updated_todo = TodoService.patch_todo(db, todo_id, todo_patch, current_user.key)
        return TodoResponse(**updated_todo.to_dict())
    except Exception:
        raise HTTPException(
            status_code=500, detail="Internal server error while updating todo"
        )


@router.delete("/{key}")
@limiter.limit("10/minute;50/hour")
def delete_todo(
    request: Request,
    response: Response,
    key: str,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Session = Depends(get_db),
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
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while deleting todo (original error message: {e})",
        )
