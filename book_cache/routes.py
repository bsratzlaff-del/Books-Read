# book_cache/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db_books
from .schemas import BookCreate, BookResponse
from . import models, open_book

router = APIRouter(prefix="/books", tags=["Books Cache & Database"])

# 1. Cache Lookup Endpoint (Checks DB cache -> tops up from Open Library to total 5)
@router.get("/lookup", response_model=list[BookResponse])
async def get_or_fetch_book(q: str, db: Session = Depends(get_db_books)):
    results = []
    
    # 1. First check database cache (matches title OR author, up to 5)
    cached_books = db.query(models.Book_Name).filter(
        (models.Book_Name.title.ilike(f"%{q}%")) |
        (models.Book_Name.author_name.ilike(f"%{q}%"))
    ).limit(5).all()
    for book in cached_books:
        results.append(book)

    # 2. If fewer than 5 in cache, fetch remaining from Open Library to reach 5 total
    if len(results) < 5:
        open_library_results = await open_book.search_books(q=q)
        
        # Track ISBNs and titles already in results to prevent duplicate entries
        existing_isbns = {b.isbn for b in results if b.isbn}
        existing_titles = {b.title.lower() for b in results if b.title}

        for ol_book in open_library_results:
            if len(results) >= 5:
                break

            # Avoid duplicates if book is already in database cache
            if ol_book.isbn and ol_book.isbn in existing_isbns:
                continue
            if ol_book.title and ol_book.title.lower() in existing_titles:
                continue

            results.append(BookResponse(
                id=None,
                title=ol_book.title or "Unknown Title",
                isbn=ol_book.isbn or "UNKNOWN",
                author_name=", ".join(ol_book.author_name) if ol_book.author_name else "Unknown"
            ))
            if ol_book.isbn:
                existing_isbns.add(ol_book.isbn)
            if ol_book.title:
                existing_titles.add(ol_book.title.lower())

    return results

    
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