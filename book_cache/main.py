from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict
from . import open_book, models
from sqlalchemy.orm import Session
from .database import Base, engine, get_db_books
from .open_book import router as book_router
from .schemas import BookCreate, BookResponse

#creates tables automatically in Postgre when app launches
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(book_router)

#updated to combine cache lookup and open library api
@app.get("/books/lookup")
async def get_or_fetch_book(title: str, db:
Session = Depends(get_db_books)):
    # First checks database cache first

    cached_book = db.query(models.Book_Name).filter(
        models.Book_Name.title.ilike(f"%{title}%")
    ).first()

    if cached_book:
        print("🎯 Cache Hit! Returning from PostgreSQL")
        return cached_book

    # Second Cache Misses, call Open Library API
    print("⚡ Cache Miss! Fetching from Open Library")
    open_library_results = await open_book.search_books(title)

    if not open_library_results:
        raise HTTPException(status_code=404, detail="Book not found anywhere")

    first_result = open_library_results[0]

    # Third, save to cache in database
    new_cached_book = models.Book_Name(
        title=first_result.title,
        isbn=first_result.isbn or "UNKNOWN",
        author_name=", ".join(first_result.author_name) 
            if first_result.author_name 
            else ""
    )
    db.add(new_cached_book)
    db.commit()
    db.refresh(new_cached_book)

    return new_cached_book

#endpoint 1: fetch all items
@app.get("/books")
def get_all_books(db:Session = Depends(get_db_books)):
    books = db.query(models.Book_Name).all()
    return books

#endpoint 2: add book to database. checks to ensure book has been added to database or not
@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED) #status code returns 201 created status code
def create_book(book_input: BookCreate, db: Session = Depends(get_db_books)):
    existing_book = (
        db.query(models.Book_Name).filter(models.Book_Name.isbn == book_input.isbn).first()
    )
    #returns error code to send information
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A book with this ISBN already exists"
        )
    #adds book using template for database
    new_book = models.Book_Name(
        title=book_input.title,
        isbn=book_input.isbn,
        author_name=book_input.author_name
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book

#endpoint 3: fetch specific item by its id, return error code if not found
@app.get("/books/{book_id}", response_model=BookResponse)
def get_book_by_id(book_id: int, db:Session = Depends(get_db_books)):
    book = db.query(models.Book_Name).filter(models.Book_Name.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Book not found"
        )
    return book

#endpoint 4: update item in database
@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id:int, book_input: BookCreate, db:Session = Depends(get_db_books)):
    db_book = db.query(models.Book_Name).filter(models.Book_Name.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Book not found"
        )

    #update attributes on the database object
    db_book.title = book_input.title
    db_book.isbn = book_input.isbn
    db_book.author_name = book_input.author_name
    

    db.commit()
    db.refresh(db_book)
    return db_book

#endpoint 5: delete item in database, throws error if book doesnt exist
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id:int, db: Session = Depends(get_db_books)):
    db_book = db.query(models.Book_Name).filter(models.Book_Name.id == book_id).first()
    
    if not db_book:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    db.delete(db_book)
    db.commit()
    return None

