from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

class Book:
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


#Pydantic request for POST data validation
class BookValidation(BaseModel):
    id: Optional[int] = None    #id is optional 
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1900, lt=2024)

    # method below to create a templete within swagger documentation. No id is needed
    class Config:
        json_schema_extra = {
            "example": {
                "title": "A new book",
                "author": "CodingwithLuke",
                "description": "Very nice",
                "rating": 4,
                "published date": 2000
            }
        }


BOOKS = [
    Book(1, "Computer Science Pro", "Author 1", "A very nice book", 5, 1999),
    Book(2, "How to kill a bird", "Author 2", "Its alright", 3, 2000),
    Book(3, "Mountaineer", "Author 3", "Very long", 3, 2000),
    Book(4, "Pokemon", "Author 4", "Too good", 1, 2012),
    Book(5, "Hello World", "Author 5", "Highly recommended", 4, 2009)
]


# This is GET
@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

# Get book with book id
@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return  book
    # http exceptions
    raise HTTPException(status_code=404, detail='Item not found')


# Get book with book rating
# Be sure if use query and now path, if path is used, fastapi might be confused and think it is passed in as book_id for method above
@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == rating:
            books_to_return.append(book)
    return books_to_return

# Make url different so fastapi doesnt get confused with rating
@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_book_by_date(date: int = Query(gt=1900, lt=2024)):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == date:
            books_to_return.append(book)
    return books_to_return


# This is POST
@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_validation: BookValidation):
    #below instantiates a variable that turns book_validation into a dictionary
    new_book = Book(**book_validation.dict())
    BOOKS.append(find_book_id(new_book))


# This creates book id that auto increments by 1 no matter what id number the user enters
def find_book_id(book: Book):
    if len(BOOKS) > 0:
        book.id = BOOKS[-1].id + 1
    else:
        book.id = 1

    return book

# This is PUT
# No validation needed for this method because it has been applied to POST
@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookValidation):
    book_changed = False
    for i in range (len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed = True

    #placed outside to avoid messing up the loop
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')


# This is Delete
@app.delete("/book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break

    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')