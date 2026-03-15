from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Todos
from database import SessionLocal
from .auth import get_current_user


# Router responsible for all todo-related operations.
# All endpoints here will start with /todos
router = APIRouter(
    prefix='/todos',
    tags=['todos']
)


# Dependency that creates a database session for each request
# and closes it automatically after the request finishes.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency aliases for cleaner endpoint definitions
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# Request schema used when creating or updating todos.
# Pydantic validates input automatically before it reaches the endpoint.
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


# Retrieve all todos belonging to the authenticated user
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):

    # Ensure the user is authenticated
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Return todos owned by the current user
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


# Retrieve a single todo by ID for the authenticated user
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Ensure users can only access their own todos
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()

    if todo_model is not None:
        return todo_model

    raise HTTPException(status_code=404, detail='Todo not found.')


# Create a new todo item for the authenticated user
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest):

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Convert request body into a SQLAlchemy model instance
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()


# Update an existing todo belonging to the authenticated user
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Ensure the todo exists and belongs to the current user
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    # Update todo fields with new values
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


# Delete a todo belonging to the authenticated user
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Ensure the todo exists and belongs to the user before deleting
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()

    db.commit()
