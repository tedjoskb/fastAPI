from typing import Optional

from fastapi import FastAPI, Body, Path, Query,HTTPException
from pydantic import BaseModel, Field
from starlette import status
from starlette.responses import JSONResponse

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating,published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self. published_date = published_date


class BookRequest(BaseModel):
    # id: int = Field(gt=0, lt=21)
    id: Optional[int] = Field(None, title='id is not needed')
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1800, lt=3000)

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'A new Book',
                'author': 'Coding with roby',
                'description': 'A new description',
                'rating': 5,
                'published_date': 2012
            }
        }


BOOKS = [
    Book(1, 'Computre Science Pro1', 'codingwithroby1', 'A very nice book!', 5,2012),
    Book(2, 'Computre Science Pro2', 'codingwithroby2', 'A very nice book!', 5,2013),
    Book(3, 'Computre Science Pro3', 'codingwithroby3', 'A very nice book!', 5,2014),
    Book(4, 'Computre Science Pro4', 'codingwithroby4', 'A very nice book!', 5,2015),
    Book(5, 'Computre Science Pro5', 'codingwithroby5', 'A very nice book!', 5,2016)
]


@app.get("/books",status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}",status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book


@app.get("/books/",status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(qt=0,lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
        else:
            books_to_return = JSONResponse(content={"message": "No Rating Books Detect!"})

    return books_to_return


@app.get("/books/publish_date/",status_code=status.HTTP_200_OK)
async def read_book_by_publish_date(published_date: int):
    books_to_return = []

    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)

    if not books_to_return:
        return JSONResponse(content={"message": "No books found for the given publish date"})
    else:
        return books_to_return


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))


def find_book_id(book: Book):
    # if len(BOOKS) > 0:
    #     book.id = BOOKS[-1].id +1
    # else:
    #     book.id = 1

    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.put("/books/update_book",status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            return {"message": "Book updated successfully"}
        break
    raise HTTPException(status_code=404, detail='Book Not Found')



@app.delete("/books/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            return {
                "status_code": 200,
                "message": "Book deleted successfully"
            }
            break
    raise HTTPException(status_code=404, detail='Book Not Found')
