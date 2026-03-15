from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

# Users table stores authentication and user profile data.
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)

    # Indicates if the user account is active
    is_active = Column(Boolean, default=True)

    # Used for role-based access control (admin / user)
    role = Column(String)


# Todos table stores tasks created by users.
class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)

    # Todo task title
    title = Column(String)

    # Description of the task
    description = Column(String)

    # Priority level (1–5)
    priority = Column(Integer)

    # Indicates whether the task is completed
    complete = Column(Boolean, default=False)

    # Foreign key linking the todo item to its owner
    owner_id = Column(Integer, ForeignKey("users.id"))
