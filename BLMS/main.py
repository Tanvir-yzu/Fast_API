
from fastapi import FastAPI,Path,HTTPException,Query,Body
import json

app = FastAPI()


def load_books_data():
    try:
        with open("books.json", "r") as f:
            books = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JSON file not found")
    return books

@app.get("/books")
def get_all_books():
    books = load_books_data()
    if books:
        return {"books": books}
    else:
        raise HTTPException(status_code=404, detail="No books found")
@app.get("/books/sort")
def sort_books(sort_by: str = Query(..., description="The field to sort by", example="book_id"), order: str = Query("asc", description="Sort order: asc or desc", example="asc")):
    valid_fields = ["book_id", "title", "author"]
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort order")
    # Case-insensitive field matching
    field_map = {f.lower(): f for f in valid_fields}
    sort_by_lower = sort_by.lower()
    if sort_by_lower not in field_map:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    sort_by = field_map[sort_by_lower]
    books = load_books_data()
    reverse = order == "desc"
    # Convert dictionary values to list for sorting
    book_list = list(books)
    # Sort numerically for numeric fields
    numeric_fields = ["book_id"]
    if sort_by in numeric_fields:
        book_list.sort(key=lambda x: int(x[sort_by]), reverse=reverse)
    else:
        book_list.sort(key=lambda x: str(x[sort_by]), reverse=reverse)
    return {"books": book_list}

@app.get("/books/{book_id}")
def get_book(book_id: int = Path(..., description="The ID of the book to get", example=1)):
    books = load_books_data()
    for book in books:
        if str(book["book_id"]) == str(book_id):
            return {"book": book}
    raise HTTPException(status_code=404, detail="Book not found")
@app.post("/creat_books")
def create_book(book: dict = Body(..., description="The book data including book_id, title, author, etc.")):
    book_id = book.get("book_id")
    if book_id is None:
        raise HTTPException(status_code=400, detail="book_id is required")
    if not isinstance(book_id, int) or book_id <= 0:
        raise HTTPException(status_code=400, detail="Book ID must be a positive integer")
    # Convert book_id to string for type consistency
    book["book_id"] = str(book_id)
    required_fields = ["title", "author"]
    missing_fields = [field for field in required_fields if field not in book]
    if missing_fields:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing_fields)}")
    books = load_books_data()
    for existing_book in books:
        if str(existing_book["book_id"]) == str(book_id):
            raise HTTPException(status_code=409, detail=f"Book with ID {book_id} already exists")
    books.append(book)
    try:
        with open("books.json", "w") as f:
            json.dump(books, f, indent=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save book data: {str(e)}")
    return {"message": "Book created successfully", "book": book}


