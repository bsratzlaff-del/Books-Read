# book_cache/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db_books
from .schemas import BookCreate, BookResponse
from . import models, open_book

router = APIRouter(prefix="/books", tags=["Books Cache & Database"])

# 1. Cache Lookup Endpoint (Checks DB cache -> calls Open Library -> saves)
@router.get("/lookup")
async def get_or_fetch_book(q: str, db: Session = Depends(get_db_books)):
    # First check database cache
    cached_book = db.query(models.Book_Name).filter(
        models.Book_Name.title.ilike(f"%{q}%")
    ).first()

    if cached_book:
        print("🎯 Cache Hit! Returning from PostgreSQL")
        return cached_book

    # Cache Miss: call Open Library API
    print("⚡ Cache Miss! Fetching from Open Library")
    open_library_results = await open_book.search_books(q=q)

    if not open_library_results:
        raise HTTPException(status_code=404, detail="Book not found anywhere")

    first_result = open_library_results[0]

    # Save to cache in database
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

# 2. Fetch all books from DB
@router.get("", response_model=list[BookResponse])
def get_all_books(db: Session = Depends(get_db_books)):
    books = db.query(models.Book_Name).all()
    return books

# 3. Add book to DB
@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_input: BookCreate, db: Session = Depends(get_db_books)):
    existing_book = (
        db.query(models.Book_Name).filter(models.Book_Name.isbn == book_input.isbn).first()
    )
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A book with this ISBN already exists"
        )
    new_book = models.Book_Name(
        title=book_input.title,
        isbn=book_input.isbn,
        author_name=book_input.author_name
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

# 4. Fetch specific book by ID
@router.get("/{book_id}", response_model=BookResponse)
def get_book_by_id(book_id: int, db: Session = Depends(get_db_books)):
    book = db.query(models.Book_Name).filter(models.Book_Name.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Book not found"
        )
    return book

# 5. Update book in DB
@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_input: BookCreate, db: Session = Depends(get_db_books)):
    db_book = db.query(models.Book_Name).filter(models.Book_Name.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    db_book.title = book_input.title
    db_book.isbn = book_input.isbn
    db_book.author_name = book_input.author_name

    db.commit()
    db.refresh(db_book)
    return db_book

# 6. Delete book from DB
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db_books)):
    db_book = db.query(models.Book_Name).filter(models.Book_Name.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    db.delete(db_book)
    db.commit()
    return None