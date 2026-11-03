#tests CRUD lifecycle and duplicate ISBN fails

import pytest
from sqlalchemy.exc import IntegrityError
from book_cache.database import SessionLocal
from book_cache import models

def test_database_crud_lifecycle():
    db = SessionLocal()
    test_isbn = "TEST-DB-12345"

    try:
        # 0. Clean up any leftover test data first
        db.query(models.Book_Name).filter(models.Book_Name.isbn == test_isbn).delete()
        db.commit()

        # 1. CREATE: Add a book to PostgreSQL
        new_book = models.Book_Name(
            title="Database Isolation Test Book",
            isbn=test_isbn,
            author_name="Database Author"
        )
        db.add(new_book)
        db.commit()
        db.refresh(new_book)

        assert new_book.id is not None, "Book should have an auto-generated ID from PostgreSQL"
        print(f"\n✅ CREATE: Stored book with ID {new_book.id}")

        # 2. READ: Query the book back from PostgreSQL
        retrieved_book = db.query(models.Book_Name).filter(
            models.Book_Name.isbn == test_isbn
        ).first()

        assert retrieved_book is not None
        assert retrieved_book.title == "Database Isolation Test Book"
        print(f"✅ READ: Retrieved '{retrieved_book.title}' by ISBN")

        # 3. UPDATE: Change title and save
        retrieved_book.title = "Updated Isolation Book Title"
        db.commit()
        db.refresh(retrieved_book)

        updated_book = db.query(models.Book_Name).filter(
            models.Book_Name.isbn == test_isbn
        ).first()
        assert updated_book.title == "Updated Isolation Book Title"
        print(f"✅ UPDATE: Successfully updated title to '{updated_book.title}'")

        # 4. DELETE: Remove the book from PostgreSQL
        db.delete(updated_book)
        db.commit()

        deleted_check = db.query(models.Book_Name).filter(
            models.Book_Name.isbn == test_isbn
        ).first()
        assert deleted_check is None
        print("✅ DELETE: Book successfully removed from PostgreSQL")

    finally:
        # Always close session
        db.close()


def test_database_duplicate_isbn_fails():
    """Tests that PostgreSQL enforces unique ISBN constraint"""
    db = SessionLocal()
    test_isbn = "TEST-DUPLICATE-ISBN"

    try:
        # Clean up first
        db.query(models.Book_Name).filter(models.Book_Name.isbn == test_isbn).delete()
        db.commit()

        # Add first book
        book1 = models.Book_Name(title="Original", isbn=test_isbn, author_name="Author")
        db.add(book1)
        db.commit()

        # Try to add a second book with identical ISBN (should fail)
        book2 = models.Book_Name(title="Duplicate", isbn=test_isbn, author_name="Author")
        db.add(book2)

        with pytest.raises(IntegrityError):
            db.commit()

        db.rollback()
        print("✅ CONSTRAINT: PostgreSQL correctly rejected duplicate ISBN!")

    finally:
        # Clean up
        db.query(models.Book_Name).filter(models.Book_Name.isbn == test_isbn).delete()
        db.commit()
        db.close()