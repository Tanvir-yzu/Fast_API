from pydantic import BaseModel, Field
from typing import Optional

class Book(BaseModel):
    book_id: int = Field(..., gt=0, description="The ID of the book, must be a positive integer")
    title: str = Field(..., min_length=1, description="The title of the book")
    author: str = Field(..., min_length=1, description="The author of the book")
    genre: Optional[str] = Field(None, description="The genre of the book")
    pages: Optional[int] = Field(None, gt=0, description="Number of pages")
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Rating out of 5")

class BookUpdate(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    genre: Optional[str] = None
    pages: Optional[int] = None
    rating: Optional[float] = None