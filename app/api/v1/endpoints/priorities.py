# app/api/v1/endpoints/todos.py
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from sqlalchemy.orm import Session
from app.schemas.priority import (
    PriorityCreate,
    PriorityUpdate,
    PriorityResponse,
    PriorityListResponse,
)
from app.services.priority_service import PriorityService
from app.api import get_current_user
from app.schemas.user import User as UserSchema
from typing import Annotated
from sqlalchemy.exc import IntegrityError

router = APIRouter()

# Schema for partial priority update


@router.get("/")
def get_priorities(
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 10
):
    skip = (page - 1) * size
    priorities = PriorityService.get_priorities(db, current_user.key, skip, size)
    total = PriorityService.get_total_priorities(db)
    return PriorityListResponse(
        priorities=[PriorityResponse(**priority.to_dict()) for priority in priorities],
        total=total,
        page=page,
        size=len(priorities),
        success=True,
    )


@router.get("/{key}")
def get_priority_by_key(
    key: str,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        priority_id = PriorityService.fetch_priority_id_by_key(db, key, current_user.key)
        priority = PriorityService.get_priority(db, priority_id, current_user.key)
        return PriorityResponse(**priority.to_dict())
    except ValueError:
        raise HTTPException(
            status_code=404, detail=f"Priority with key {key} not found"
        )


@router.post("/")
def create_priority(
    priority: PriorityCreate, 
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Session = Depends(get_db)    
):
    try:
        priority = PriorityService.create_priority(db, priority, current_user.key)
        return PriorityResponse(**priority.to_dict())
    except IntegrityError as e:
        if "uq_priority_user_order" in str(e):
            raise HTTPException(
                status_code=400, detail=f"Priority order already exists"
            )
        elif "uq_priority_user_name" in str(e):
            raise HTTPException(
                status_code=400, detail=f"Priority name already exists"
            )
        else:
            raise HTTPException(
                status_code=500, detail="Internal server error while creating priority"
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{key}")
def update_priority(
    key: str, 
    priority: PriorityUpdate, 
    current_user: Annotated[UserSchema, Depends(get_current_user)], 
    db: Session = Depends(get_db)
):
    try:
        priority_id = PriorityService.fetch_priority_id_by_key(db, key, current_user.key)
    except ValueError:
        raise HTTPException(
            status_code=404, detail=f"Priority with key {key} not found"
        )

    try:
        priority = PriorityService.update_priority(db, priority_id, priority, current_user.key)
        return PriorityResponse(**priority.to_dict())
    except IntegrityError as e:
        if "uq_priority_user_order" in str(e):
            raise HTTPException(
                status_code=400, detail=f"Priority order already exists"
            )
        elif "uq_priority_user_name" in str(e):
            raise HTTPException(
                status_code=400, detail=f"Priority name already exists"
            )
        else:
            raise HTTPException(
                status_code=500, detail="Internal server error while updating priority"
            )
    except Exception:
        raise HTTPException(
            status_code=500, detail="Internal server error while updating priority"
        )


@router.patch("/{key}")
def patch_priority(
    key: str, 
    priority_patch: dict, 
    current_user: Annotated[UserSchema, Depends(get_current_user)], 
    db: Session = Depends(get_db)
):
    try:
        priority_id = PriorityService.fetch_priority_id_by_key(db, key, current_user.key)
    except IntegrityError as e:
        if "uq_priority_user_order" in str(e):
            raise HTTPException(
                status_code=400, detail=f"Priority order already exists"
            )
        elif "uq_priority_user_name" in str(e):
            raise HTTPException(
                status_code=400, detail=f"Priority name already exists"
            )
        else:
            raise HTTPException(
                status_code=500, detail="Internal server error while patching priority"
            )
    except ValueError:
        raise HTTPException(
            status_code=404, detail=f"Priority with key {key} not found"
        )

    try:
        # Only update fields that are provided
        updated_priority = PriorityService.patch_priority(
            db, priority_id, priority_patch, current_user.key
        )
        return PriorityResponse(**updated_priority.to_dict())
    except Exception:
        raise HTTPException(
            status_code=500, detail="Internal server error while updating priority"
        )


@router.delete("/{key}")
def delete_priority(
    key: str, 
    current_user: Annotated[UserSchema, Depends(get_current_user)], 
    db: Session = Depends(get_db)
):
    try:
        priority_id = PriorityService.fetch_priority_id_by_key(db, key, current_user.key)
        if PriorityService.delete_priority(db, priority_id, current_user.key):
            return {"message": "Priority deleted successfully"}
        else:
            raise HTTPException(
                status_code=500, detail="Internal server error while deleting priority"
            )
    except ValueError:
        raise HTTPException(
            status_code=404, detail=f"Priority with key {key} not found"
        )
