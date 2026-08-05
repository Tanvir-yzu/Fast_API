import json
from fastapi import HTTPException

DATA_FILE = "books.json"

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