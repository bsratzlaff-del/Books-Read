#how the information gets across the backend

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db_books
from .schemas import BookCreate, BookResponse
from . import models, open_book

# 1. Create a Router with a shared prefix:
router = APIRouter(prefix="/books", tags=["Books Cache & Database"])

# 2. All your endpoints live here:
@router.get("/lookup")
async def get_or_fetch_book(q: str, db: Session = Depends(get_db_books)):
    # ... your cache lookup logic ...
    pass

@router.get("", response_model=list[BookResponse])
def get_all_books(db: Session = Depends(get_db_books)):
    return db.query(models.Book_Name).all()

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_input: BookCreate, db: Session = Depends(get_db_books)):
    # ... create book logic ...
    pass

@router.get("/{book_id}", response_model=BookResponse)
def get_book_by_id(book_id: int, db: Session = Depends(get_db_books)):
    # ... get by id logic ...
    pass

@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_input: BookCreate, db: Session = Depends(get_db_books)):
    # ... update book logic ...
    pass

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db_books)):
    # ... delete book logic ...
    pass