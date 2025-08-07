# app/api/v1/endpoints/todos.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_todos():
    return {"todos": []}

@router.post("/")
def create_todo():
    return {"message": "Created"}