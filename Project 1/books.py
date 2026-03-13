from fastapi import Body, FastAPI

# Create the FastAPI app
app = FastAPI()

# Temporary in-memory data store
# In real projects, this would usually come from a database
BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]

# GET all books
@app.get("/books")
async def read_all_books():
    return BOOKS


# GET one book using a path parameter
# Example: /books/Title One
@app.get("/books/title/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        # casefold() makes comparison case-insensitive
        if book.get('title').casefold() == book_title.casefold():
            return book


# GET books by category using a query parameter
# Example: /books/?category=math
@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


# GET books by author using a query parameter
# Example: /books/byauthor/?author=Author Two
@app.get("/books/byauthor/")
async def read_books_by_author_path(author: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold():
            books_to_return.append(book)

    return books_to_return


# GET books by author (path parameter) and category (query parameter)
# Example: /books/Author Two/?category=math
@app.get("/books/author/{book_author}")
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
                book.get('category').casefold() == category.casefold():
            books_to_return.append(book)

    return books_to_return


# POST creates a new book
# Body() reads JSON data sent in the request body
@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)


# PUT updates an existing book by matching title
# If titles match, replace old book data with updated data
@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book


# DELETE removes a book by title
@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            BOOKS.pop(i)
            break