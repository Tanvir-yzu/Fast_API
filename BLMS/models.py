from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float
from database import Base


# ── SQLAlchemy ORM model (for Alembic / DB) ────────────────────────────────

class BookModel(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=True)
    pages = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)


# ── Pydantic schemas (for API request/response validation) ─────────────────

class Book(BaseModel):
    book_id: int = Field(..., gt=0, description="The ID of the book, must be a positive integer")
    title: str = Field(..., min_length=1, description="The title of the book")
    author: str = Field(..., min_length=1, description="The author of the book")
    genre: Optional[str] = Field(None, description="The genre of the book")
    pages: Optional[int] = Field(None, gt=0, description="Number of pages")
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Rating out of 5")


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1)
    genre: Optional[str] = None
    pages: Optional[int] = Field(None, gt=0)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)