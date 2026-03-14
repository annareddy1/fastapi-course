from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

# Create the FastAPI application instance
app = FastAPI()


class Book:
    """
    Plain Python class representing a book entity stored in memory.

    This acts like a temporary database model for this demo project.
    """
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    """
    Pydantic request model used to validate incoming request bodies.

    This ensures the API only accepts properly structured and valid book data.
    """
    id: Optional[int] = Field(default=None, description="ID is not needed when creating a new book")
    title: str = Field(min_length=3, description="Book title must be at least 3 characters long")
    author: str = Field(min_length=1, description="Author name must not be empty")
    description: str = Field(min_length=1, max_length=100, description="Book description must be 1 to 100 characters long")
    rating: int = Field(gt=0, lt=6, description="Rating must be between 1 and 5")
    published_date: int = Field(gt=1999, lt=2031, description="Published year must be between 2000 and 2030")

    # Extra schema metadata shown in Swagger/OpenAPI docs
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of a book",
                "rating": 5,
                "published_date": 2029
            }
        }
    }


# In-memory list acting as a temporary database
BOOKS = [
    Book(1, 'Computer Science Pro', 'codingwithroby', 'A very nice book!', 5, 2030),
    Book(2, 'Be Fast with FastAPI', 'codingwithroby', 'A great book!', 5, 2030),
    Book(3, 'Master Endpoints', 'codingwithroby', 'An awesome book!', 5, 2029),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2, 2028),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3, 2027),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1, 2026)
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    """
    Retrieve all books from the in-memory collection.
    """
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    """
    Retrieve a single book by its ID.

    Raises:
        HTTPException: If the book ID does not exist.
    """
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Item not found')


@app.get("/books/by-rating", status_code=status.HTTP_200_OK)
async def read_books_by_rating(book_rating: int = Query(gt=0, lt=6)):
    """
    Retrieve all books that match the given rating.
    """
    books_to_return = []

    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)

    return books_to_return


@app.get("/books/publish", status_code=status.HTTP_200_OK)
async def read_books_by_publish_date(published_date: int = Query(gt=1999, lt=2031)):
    """
    Retrieve all books that match the given published year.
    """
    books_to_return = []

    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)

    return books_to_return


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    """
    Create a new book and add it to the in-memory collection.

    The ID is automatically assigned.
    """
    new_book = Book(**book_request.model_dump())
    new_book = find_book_id(new_book)
    BOOKS.append(new_book)
    return new_book


def find_book_id(book: Book):
    """
    Assign the next available ID to a new book.

    If the list is empty, start with ID = 1.
    Otherwise, assign the last book's ID + 1.
    """
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    """
    Update an existing book.

    Raises:
        HTTPException: If the book ID is missing or not found.
    """
    if book.id is None:
        raise HTTPException(status_code=400, detail="ID must be provided for update")

    book_changed = False

    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = Book(**book.model_dump())
            book_changed = True
            break

    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    """
    Delete a book by its ID.

    Raises:
        HTTPException: If the book ID does not exist.
    """
    book_changed = False

    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break

    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')