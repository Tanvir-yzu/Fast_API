from fastapi import APIRouter, Path, HTTPException, Query
from models import Book, BookUpdate
from database import load_books_data, save_books_data

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("")
def get_all_books():
    books = load_books_data()
    if not books:
        raise HTTPException(status_code=404, detail="No books found")
    return {"books": books}


@router.get("/sort")
def sort_books(
    sort_by: str = Query(..., description="Field to sort by", example="book_id"),
    order: str = Query("asc", description="Sort order: asc or desc"),
):
    valid_fields = ["book_id", "title", "author"]
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort order")

    field_map = {f.lower(): f for f in valid_fields}
    if sort_by.lower() not in field_map:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    sort_by = field_map[sort_by.lower()]
    books = load_books_data()
    reverse = order == "desc"

    book_list = list(books)
    if sort_by == "book_id":
        book_list.sort(key=lambda x: int(x["book_id"]), reverse=reverse)
    else:
        book_list.sort(key=lambda x: str(x[sort_by]), reverse=reverse)

    return {"books": book_list}


@router.get("/{book_id}")
def get_book(book_id: int = Path(..., gt=0)):
    books = load_books_data()
    for book in books:
        if int(book["book_id"]) == book_id:
            return {"book": book}
    raise HTTPException(status_code=404, detail="Book not found")


@router.post("", status_code=201)
def create_book(book: Book):
    books = load_books_data()

    for existing_book in books:
        if int(existing_book["book_id"]) == book.book_id:
            raise HTTPException(
                status_code=409,
                detail=f"Book with ID {book.book_id} already exists",
            )

    new_book = book.model_dump()
    books.append(new_book)
    save_books_data(books)
    return {"message": "Book created successfully", "book": new_book}


@router.put("/{book_id}")
def update_book(book_id: int, book_update: BookUpdate):
    books = load_books_data()
    for existing_book in books:
        if int(existing_book["book_id"]) == book_id:
            update_data = book_update.model_dump(exclude_unset=True)
            existing_book.update(update_data)
            save_books_data(books)
            return {"message": "Book updated successfully", "book": existing_book}

    raise HTTPException(status_code=404, detail="Book not found")


@router.delete("/{book_id}")
def delete_book(book_id: int):
    books = load_books_data()
    for book in books:
        if int(book["book_id"]) == book_id:
            books.remove(book)
            save_books_data(books)
            return {"message": "Book deleted successfully"}

    raise HTTPException(status_code=404, detail="Book not found")