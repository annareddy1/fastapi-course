from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos, admin, users

# Initialize FastAPI application
app = FastAPI()

# Create database tables based on the ORM models.
# In production systems migrations (Alembic) are typically used instead.
models.Base.metadata.create_all(bind=engine)

# Register API routers for different parts of the application.
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
