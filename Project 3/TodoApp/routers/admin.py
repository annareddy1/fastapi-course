from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Todos
from database import SessionLocal
from .auth import get_current_user

# Router for admin-specific endpoints.
# All routes in this router will start with /admin
router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


# Dependency to create and manage a database session.
# A new session is created for each request and closed after the request finishes.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency injection type aliases for cleaner endpoint definitions
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# Admin endpoint to retrieve all todos in the system.
# Only users with the "admin" role are allowed to access this endpoint.
@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    # Verify the requesting user is authenticated and has admin privileges
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Return all todo items from the database
    return db.query(Todos).all()


# Admin endpoint to delete any todo item by its ID.
# This operation bypasses ownership checks and is restricted to admin users.
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    # Ensure the user is authenticated and has admin privileges
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Attempt to locate the todo item in the database
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    # If the todo does not exist, return a 404 error
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    # Delete the todo item
    db.query(Todos).filter(Todos.id == todo_id).delete()

    # Commit the transaction to persist the deletion
    db.commit()

    return {"message": "Todo successfully deleted by admin"}
