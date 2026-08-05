import json
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATA_FILE = "books.json"

# SQLAlchemy setup for Alembic migrations
SQLALCHEMY_DATABASE_URL = "sqlite:///./books.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# JSON-based helpers (backward compatibility)
def load_books_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JSON file not found")


def save_books_data(books):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(books, f, indent=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save book data: {str(e)}")