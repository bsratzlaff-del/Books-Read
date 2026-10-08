from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict
from book_cache import models
from sqlalchemy.orm import Session
from book_cache.database import Base, engine, get_db_books

#creates tables automatically in Postgre when app launches
Base.metadata.create_all(bind=engine)

app = FastAPI()

#defines structural template for data coming in 
class ItemCreate(BaseModel):
    title: str
    isbn: str
    first_author: str
    last_author: str

#defines structural template for sending data back to user
class ItemResponse(ItemCreate):
    id:int
    model_config = ConfigDict(from_attributes=True)

#endpoint 1: fetch all items
@app.get("/books")
def get_all_books(db:Session = Depends(get_db_books)):
    books = db.query(models.Item).all()
    return books

#endpoint 2: add book to database. checks to ensure book has been added to database or not
@app.post("/books", response_model=ItemResponse, status_code=status.HTTP_201_CREATED) #status code returns 201 created status code
def create_book(book_input: ItemCreate, db: Session = Depends(get_db_books)):
    existing_book = (
        db.query(models.Item).filter(models.Item.isbn == book_input.isbn).first()
    )
    #returns error code to send information
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A book with this ISBN already exists"
        )
    #adds book using template for database
    new_book = models.Item(
        title=book_input.title,
        isbn=book_input.isbn,
        first_author=book_input.first_author,
        last_author=book_input.last_author,
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book

#endpoint 3: fetch specific item by its id, return error code if not found
@app.get("/books/{book_id}", response_model=ItemResponse)
def get_book_by_id(book_id: int, db:Session = Depends(get_db_books)):
    book = db.query(models.Item).filter(models.Item.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code == status.HTTP_404_NOT_FOUND, 
            detail = "Book not found"
        )
    return book

#endpoint 4: update item in database
@app.put("/books/{book_id}", response_model=ItemResponse)
def update_book(book_id:int, book_input: ItemCreate, db:Session = Depends(get_db_books)):
    db_book = db.query(models.Item).filter(models.Item.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code==status.HTTP_404_NOT_FOUND,
            detail = "Book not found"
        )

    #update attributes on the database object
    db_book.title = book_input.title
    db_book.isbn = book_input.isbn
    db_book.first_author = book_input.first_author
    db_book.last_author = book_input.last_author

    db.commit()
    db.refresh(db_book)
    return db_book

#endpoint 5: delete item in database, throws error if book doesnt exist
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id:int, db: Session = Depends(get_db_books)):
    db_book = db.query(models.Item).filter(models.Item.id == book_id).first()
    
    if not db_book:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    db.delete(db_book)
    db.commit()
    return None

