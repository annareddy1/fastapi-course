from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Users
from database import SessionLocal
from .auth import get_current_user
from passlib.context import CryptContext


# Router responsible for user profile and account-related operations
router = APIRouter(
    prefix='/user',
    tags=['user']
)


# Dependency to create and manage a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency aliases for cleaner endpoint definitions
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# Password hashing configuration using bcrypt
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# Request schema used when a user wants to change their password
class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


# Retrieve the currently authenticated user's profile information
@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):

    # Ensure the request is authenticated
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Return user record from the database
    return db.query(Users).filter(Users.id == user.get('id')).first()


# Endpoint allowing an authenticated user to change their password
@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency,
                          user_verification: UserVerification):

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Retrieve the user record from the database
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    # Verify the current password before allowing a change
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')

    # Hash and store the new password
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)

    db.add(user_model)
    db.commit()
