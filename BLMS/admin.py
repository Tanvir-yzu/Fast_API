from sqladmin import Admin, ModelView
from database import engine
from models import BookModel


class BookAdmin(ModelView, model=BookModel):
    column_list = [
        BookModel.book_id,
        BookModel.title,
        BookModel.author,
        BookModel.genre,
        BookModel.pages,
        BookModel.rating,
    ]
    column_searchable_list = [BookModel.title, BookModel.author]
    column_sortable_list = [BookModel.book_id, BookModel.title, BookModel.author]
    column_default_sort = (BookModel.book_id, True)  # ascending
    form_create_rules = ["title", "author", "genre", "pages", "rating"]
    form_edit_rules = ["title", "author", "genre", "pages", "rating"]
    name = "Book"
    name_plural = "Books"
    icon = "fa-solid fa-book"


def setup_admin(app):
    admin = Admin(app, engine)
    admin.add_view(BookAdmin)
    return admin