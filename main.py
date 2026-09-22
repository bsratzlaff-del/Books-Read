from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

#demo database entries
book_names_db = {
    1: {"name": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    2: {"name": "To Kill a Mockingbird", "author": "Harper Lee"}
}

#defines structural template for data 
class Item(BaseModel):
    name: str
    author: str

#endpoint 1: fetch all items
@app.get("/books")
def get_items():
    return book_names_db

#endpoint 2: fetch specific item by its id
@app.get("/books/{book_id}")
def get_item_by_id(book_id: int):
    if book_id in book_names_db:
        return book_names_db[book_id]
    return {"error": "Book not found"}

#endpoint 3: add item to database
@app.post("/books", status_code=201) #status code returns 201 created status code
def create_book(book: Item):
    new_id = max(book_names_db.keys(), default = 0) + 1
    book_names_db[new_id] = book.model_dump()
    return {"message": "item added successfully", "id": new_id}


#endpoint 4: update item in database
@app.put("/books/{book_id}")
def update_books(book_id:int, book: Item):
    return {
        "book_id": book_id,
        "book": book,
    }

#endpoint 5: delete item in database
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_books(book_id:int):
    if book_id not in book_names_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    del book_names_db[book_id]

