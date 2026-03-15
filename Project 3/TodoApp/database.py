from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database connection string.
# This points to a SQLite database file stored locally in the project directory.
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"

# Create the SQLAlchemy engine that manages the connection to the database.
# check_same_thread=False is required for SQLite when used with FastAPI.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal is a database session factory.
# Each API request will create its own session using this.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class used for defining SQLAlchemy ORM models.
Base = declarative_base()
