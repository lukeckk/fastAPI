from fastapi import FastAPI, Body

app = FastAPI()

BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]


# GET METHOD STARTS HERE

@app.get("/books")
async def read_all_books():
    return BOOKS


# Use of path parameter to create a dynamic get method that allows user to select which book to get by passing in the paramenter
# Must be created after /books so /books can be called when user is selecting all books
# THIS USES PATH
@app.get("/books/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book


# Use of ? in the url to select specific category
# The method below allows users to select different authors and query the category of the author
# There is no parameter in the end of url means anything that is passed in will be converted into whatever parameter we have in the function which is 'category'
# http://127.0.0.1:8000/book/?category={category}
# THIS USES QUERY
@app.get("/book/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


# THIS USES PATH AND QUERY
# http://127.0.0.1:8000/books/author%20two/?category=math
@app.get("/books/{book_author}/")
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() \
                and book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


# POST METHOD STARTS HERE
# THIS USES QUERY
#first import body (body only works with .post() method)

# Adding a new book using body
# Must use " when adding
@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)


# PUT METHOD STARTS HERE
# THIS USES QUERY

# Must use for loop with index
@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for index in range (len(BOOKS)):
        if BOOKS[index].get("title").casefold() == updated_book.get("title").casefold():
            BOOKS[index] = updated_book

# Delete METHOD STARTS HERE
# THIS USES PATH
@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title:str):
    for i in range (len(BOOKS)):
        if BOOKS[i].get("title").casefold() == book_title.casefold():
            BOOKS.pop(i)
            break
