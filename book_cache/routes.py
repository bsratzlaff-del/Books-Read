# book_cache/routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from .database import get_db_books
from .schemas import BookCreate, BookResponse
from . import models, open_book

router = APIRouter(prefix="/books", tags=["Books Cache & Database"])

# 1. Cache Lookup Endpoint (Paginated: Checks DB cache -> tops up from Open Library)
@router.get("/lookup", response_model=list[BookResponse])
async def get_or_fetch_book(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(5, ge=1, le=20, description="Items per page"),
    db: Session = Depends(get_db_books)
):
    results = []
    global_offset = (page - 1) * limit

    # Count matching books in database cache
    cache_query = db.query(models.Book_Name).filter(
        (models.Book_Name.title.ilike(f"%{q}%")) |
        (models.Book_Name.author_name.ilike(f"%{q}%"))
    )
    total_cached = cache_query.count()

    # 1. Pull from DB cache if this page range overlaps cached records
    if global_offset < total_cached:
        cached_books = cache_query.offset(global_offset).limit(limit).all()
        for book in cached_books:
            results.append(book)

    # 2. If fewer than limit in results, top up from Open Library
    if len(results) < limit:
        needed = limit - len(results)

        # Calculate Open Library offset:
        # If past the cached records, offset into Open Library by the difference; otherwise start at 0
        ol_offset = max(0, global_offset - total_cached)

        open_library_results = await open_book.search_books(
            q=q,
            offset=ol_offset,
            limit=needed + 10
        )
        
        # Track ISBNs and titles already in results to prevent duplicate entries
        existing_isbns = {b.isbn for b in results if b.isbn}
        existing_titles = {b.title.lower() for b in results if b.title}

        for ol_book in open_library_results:
            if len(results) >= limit:
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