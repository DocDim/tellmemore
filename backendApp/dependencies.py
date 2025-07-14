from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import os
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
# Added 'options=project%3Dep-square-unit-a8cybfqv' to explicitly set the project slug for Neon.tech pooler.
DATABASE_URL="postgresql://neondb_owner:npg_37ogzmSbAFwj@ep-square-unit-a8cybfqv-pooler.eastus2.azure.neon.tech:5432/neondb?sslmode=require&options=endpoint%3Dep-square-unit-a8cybfqv"

# SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# SessionLocal for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for SQLAlchemy declarative models
Base = declarative_base()

# Dependency to get DB session
@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for FastAPI endpoints
def get_db():
    with get_db_session() as db:
        yield db
