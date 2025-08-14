# app/api/v1/api.py
from fastapi import APIRouter, Depends
from app.api.v1.endpoints import todos, priorities, token, user
from app.api import get_current_user

api_router = APIRouter()
api_router.include_router(todos.router, prefix="/todos", tags=["todos"], dependencies=[Depends(get_current_user)])
api_router.include_router(priorities.router,
                          prefix="/priorities", tags=["priorities"], dependencies=[Depends(get_current_user)])
api_router.include_router(token.router, tags=["token"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
