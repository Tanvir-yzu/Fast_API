import os
import json
import sys
import tempfile
import shutil

# Ensure the BLMS package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# --- Fixtures ---

TEST_DATA = [
    {"book_id": 1, "title": "Alpha", "author": "Zoe", "genre": "fiction", "pages": 100, "rating": 4.0},
    {"book_id": 2, "title": "Beta", "author": "Yara", "genre": "science", "pages": 200, "rating": 3.5},
    {"book_id": 3, "title": "Gamma", "author": "Xander", "genre": "history", "pages": 150, "rating": 4.5},
]

CURRENT_DATA_FILE = None  # will be set by setup_module


def setup_module():
    """Backup the real books.json and replace it with test data."""
    global CURRENT_DATA_FILE
    from database import DATA_FILE

    # Resolve the absolute path that the app will use
    CURRENT_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", DATA_FILE)
    CURRENT_DATA_FILE = os.path.normpath(CURRENT_DATA_FILE)

    # If real file exists, back it up
    if os.path.exists(CURRENT_DATA_FILE):
        backup = CURRENT_DATA_FILE + ".bak"
        shutil.copy2(CURRENT_DATA_FILE, backup)

    # Write test data
    with open(CURRENT_DATA_FILE, "w") as f:
        json.dump(TEST_DATA, f)


def teardown_module():
    """Restore the original books.json if a backup exists."""
    backup = CURRENT_DATA_FILE + ".bak"
    if os.path.exists(backup):
        shutil.move(backup, CURRENT_DATA_FILE)


# --- Tests for GET /books ---

class TestGetAllBooks:
    def test_get_all_books_success(self):
        resp = client.get("/books")
        assert resp.status_code == 200
        data = resp.json()
        assert "books" in data
        assert len(data["books"]) == 3

    def test_get_all_books_empty(self):
        # Temporarily write empty list
        with open(CURRENT_DATA_FILE, "w") as f:
            json.dump([], f)
        resp = client.get("/books")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "No books found"
        # Restore test data
        with open(CURRENT_DATA_FILE, "w") as f:
            json.dump(TEST_DATA, f)


# --- Tests for GET /books/sort ---

class TestSortBooks:
    def test_sort_by_book_id_asc(self):
        resp = client.get("/books/sort?sort_by=book_id&order=asc")
        assert resp.status_code == 200
        ids = [b["book_id"] for b in resp.json()["books"]]
        assert ids == [1, 2, 3]

    def test_sort_by_book_id_desc(self):
        resp = client.get("/books/sort?sort_by=book_id&order=desc")
        assert resp.status_code == 200
        ids = [b["book_id"] for b in resp.json()["books"]]
        assert ids == [3, 2, 1]

    def test_sort_by_title_asc(self):
        resp = client.get("/books/sort?sort_by=title&order=asc")
        assert resp.status_code == 200
        titles = [b["title"] for b in resp.json()["books"]]
        assert titles == ["Alpha", "Beta", "Gamma"]

    def test_sort_by_title_desc(self):
        resp = client.get("/books/sort?sort_by=title&order=desc")
        assert resp.status_code == 200
        titles = [b["title"] for b in resp.json()["books"]]
        assert titles == ["Gamma", "Beta", "Alpha"]

    def test_sort_by_author_asc(self):
        resp = client.get("/books/sort?sort_by=author&order=asc")
        assert resp.status_code == 200
        authors = [b["author"] for b in resp.json()["books"]]
        assert authors == ["Xander", "Yara", "Zoe"]

    def test_sort_invalid_field(self):
        resp = client.get("/books/sort?sort_by=invalid&order=asc")
        assert resp.status_code == 400
        assert "Invalid sort field" in resp.json()["detail"]

    def test_sort_invalid_order(self):
        resp = client.get("/books/sort?sort_by=book_id&order=invalid")
        assert resp.status_code == 400
        assert "Invalid sort order" in resp.json()["detail"]


# --- Tests for GET /books/{book_id} ---

class TestGetBook:
    def test_get_book_found(self):
        resp = client.get("/books/1")
        assert resp.status_code == 200
        assert resp.json()["book"]["book_id"] == 1
        assert resp.json()["book"]["title"] == "Alpha"

    def test_get_book_not_found(self):
        resp = client.get("/books/999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Book not found"

    def test_get_book_invalid_id(self):
        resp = client.get("/books/-1")
        assert resp.status_code == 422

    def test_get_book_zero_id(self):
        resp = client.get("/books/0")
        assert resp.status_code == 422


# --- Tests for POST /books ---

class TestCreateBook:
    def test_create_book_success(self):
        new_book = {
            "book_id": 100,
            "title": "New Book",
            "author": "New Author",
            "genre": "fiction",
            "pages": 300,
            "rating": 4.0,
        }
        resp = client.post("/books", json=new_book)
        assert resp.status_code == 201
        data = resp.json()
        assert data["message"] == "Book created successfully"
        assert data["book"]["book_id"] == 100

        # Verify it was persisted
        resp2 = client.get("/books/100")
        assert resp2.status_code == 200

        # Cleanup
        client.delete("/books/100")

    def test_create_book_duplicate_id(self):
        resp = client.post("/books", json={"book_id": 1, "title": "Dup", "author": "Dup"})
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]

    def test_create_book_missing_required_fields(self):
        resp = client.post("/books", json={"book_id": 200})
        assert resp.status_code == 422

    def test_create_book_invalid_id_type(self):
        resp = client.post("/books", json={"book_id": "abc", "title": "T", "author": "A"})
        assert resp.status_code == 422


# --- Tests for PUT /books/{book_id} ---

class TestUpdateBook:
    def test_update_book_partial_success(self):
        # First create a book
        client.post("/books", json={"book_id": 50, "title": "Original", "author": "Original Author"})

        # Partial update — only change title
        resp = client.put("/books/50", json={"title": "Updated Title"})
        assert resp.status_code == 200
        assert resp.json()["book"]["title"] == "Updated Title"
        assert resp.json()["book"]["author"] == "Original Author"

        # Cleanup
        client.delete("/books/50")

    def test_update_book_full_success(self):
        client.post("/books", json={"book_id": 51, "title": "T", "author": "A", "pages": 100})
        resp = client.put("/books/51", json={"title": "New T", "author": "New A", "pages": 200, "rating": 4.5})
        assert resp.status_code == 200
        updated = resp.json()["book"]
        assert updated["title"] == "New T"
        assert updated["author"] == "New A"
        assert updated["pages"] == 200
        assert updated["rating"] == 4.5
        client.delete("/books/51")

    def test_update_book_not_found(self):
        resp = client.put("/books/999", json={"title": "Nope"})
        assert resp.status_code == 404

    def test_update_book_invalid_data(self):
        resp = client.put("/books/1", json={"pages": -5})
        assert resp.status_code == 422


# --- Tests for DELETE /books/{book_id} ---

class TestDeleteBook:
    def test_delete_book_success(self):
        client.post("/books", json={"book_id": 70, "title": "Delete Me", "author": "Me"})
        resp = client.delete("/books/70")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Book deleted successfully"

        # Verify it's gone
        resp2 = client.get("/books/70")
        assert resp2.status_code == 404

    def test_delete_book_not_found(self):
        resp = client.delete("/books/999")
        assert resp.status_code == 404