from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

# Router responsible for authentication-related endpoints
# All routes in this file will be prefixed with /auth
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# Secret key used to sign and verify JWT tokens
# In production this should be stored in environment variables
SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'

# JWT signing algorithm
ALGORITHM = 'HS256'

# Password hashing configuration using bcrypt
# This ensures passwords are never stored in plaintext
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# OAuth2 bearer token scheme used for authentication
# FastAPI will extract the token from the Authorization header
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


# Request schema for user registration
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


# Response schema returned after successful login
class Token(BaseModel):
    access_token: str
    token_type: str


# Dependency that provides a database session for each request
# A new session is opened and automatically closed after the request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Type alias for cleaner dependency injection in route functions
db_dependency = Annotated[Session, Depends(get_db)]


# Authenticate a user by verifying username and password
# Returns the user object if authentication succeeds
def authenticate_user(username: str, password: str, db):
    # Retrieve user from database
    user = db.query(Users).filter(Users.username == username).first()

    # Return False if user does not exist
    if not user:
        return False

    # Verify password against hashed password stored in database
    if not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


# Create a JWT access token containing user identity and role
# This token will be used for authenticated requests
def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    # Payload stored inside the JWT token
    encode = {
        'sub': username,
        'id': user_id,
        'role': role
    }

    # Token expiration time
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})

    # Generate encoded JWT token
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# Dependency used by protected endpoints to retrieve the current user
# The token is extracted from the Authorization header
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        # Decode and verify JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract user data from token payload
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')

        # Validate required fields
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user.'
            )

        # Return user information used in protected routes
        return {
            'username': username,
            'id': user_id,
            'user_role': user_role
        }

    # Triggered if token is invalid or expired
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.'
        )


# Endpoint for registering a new user
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    # Create a new user model instance
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,

        # Hash password before storing it for security
        hashed_password=bcrypt_context.hash(create_user_request.password),

        is_active=True
    )

    # Save user to database
    db.add(create_user_model)
    db.commit()


# Endpoint for user login
# Returns a JWT access token used for authenticated API requests
@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency):
    # Verify username and password
    user = authenticate_user(form_data.username, form_data.password, db)

    # Raise error if authentication fails
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.'
        )

    # Generate JWT token valid for 20 minutes
    token = create_access_token(
        user.username,
        user.id,
        user.role,
        timedelta(minutes=20)
    )

    return {
        'access_token': token,
        'token_type': 'bearer'
    }
