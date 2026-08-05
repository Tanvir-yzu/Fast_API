from fastapi import FastAPI
from database import engine, Base
from models import BookModel  # noqa: F401 — ensure models are registered
from routers import books
from admin import setup_admin

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Modern Book Management API",
    version="2.0.0",
    description="A cleanly structured FastAPI application"
)

# Include the books router
app.include_router(books.router)

# Setup SQLAdmin (admin panel at /admin)
setup_admin(app)

@app.get("/")
def root():
    return {
        "message": "Welcome to the Modern FastAPI Book App!",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "endpoints": {
            "GET /books": "List all books",
            "GET /books/{book_id}": "Get a single book by ID",
            "GET /books/sort?sort_by=...&order=...": "Sort books by field (asc/desc)",
            "POST /books": "Create a new book",
            "PUT /books/{book_id}": "Update an existing book",
            "DELETE /books/{book_id}": "Delete a book",
        },
        "version": "2.0.0",
    }