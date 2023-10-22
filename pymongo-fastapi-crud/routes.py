# Create new endpoints for storing/getting data from the db
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Book, BookUpdate

router = APIRouter()

@router.post("/", response_description="Create a new book", status_code=status.HTTP_201_CREATED, response_model=Book)
def create_book(request: Request, book: Book = Body(...)):
    book = jsonable_encoder(book)
    # does the request.app.database come from the main.py app? 
    new_book = request.app.database["books"].insert_one(book)
    created_book = request.app.database["books"].find_one(
        {"_id": new_book.inserted_id}
    )

    return created_book

# GET /book
# get list of all documents in the book collection 
@router.get("/", response_description="List all books", response_model=List[Book])
def list_books(request: Request):
    # find pattern with key:value 
    db.test.find({"hello": "world"}) 
    books = list(request.app.database["books"].find(limit=100))
    return books

# GET /book/{id}
# get book data using specific book {id}
@router.get("/{id}", response_description="Get single book by id", response_model=Book)
def find_book(id: str, request: Request):
    # here we assign the value from the find_one query to the book variable 
    if (book := request.app.database["books"].find_one({"_id": id})) is not None:
        return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found") 

# PUT /book/{id}
# update and put the book into the db 
@router.put("/{id}", response_description="Update a book", response_model=Book)
def update_book(id: str, request: Request, book: BookUpdate = Body(...)):
    # first go through book items and don't allow None items
    book = {k: v for k, v in book.dict().items() if v is not None}
    print("Update book:")
    print(book)
    if len(book) >= 1:
        update_result = request.app.database["books"].update_one(
            {"_id": id},
            {"$set": book})
        
        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")
    if (existing_book := request.app.database["books"].find_one({"_id": id})) is not None:
        return existing_book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found") 

# DELETE /book/{id}
# Delete book by {id} for deleting a single book
@router.delete("/{id}", response_description="Delete a book")
def delete_book(id: str, request: Request, response: Response):
    delete_result = request.app.database["books"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        resposne.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")
