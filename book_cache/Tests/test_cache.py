#test to ensure the code is properly pulling cache first
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from book_cache.main import app
from book_cache.database import SessionLocal
from book_cache import models
from book_cache import routes


client = TestClient(app)

def test_cache_hit():
    #First Seeds a book directly into database
    db = SessionLocal()
    test_isbn = "999-TEST-CACHE"

#clean up test from previous runs
    db.query(models.Book_Name).filter(models.Book_Name.isbn == test_isbn).delete()
    db.commit()

    seeded_book = models.Book_Name(
        title = "Cache Test Odyssey",
        isbn = test_isbn,
        author_name = "Test Author"
    )
    db.add(seeded_book)
    db.commit()
    db.close()

    #Second, mock open_book.search_books to track whether or not it gets called
    with patch("book_cache.routes.open_book.search_books", new_callable=AsyncMock) as mock_search:
        #Third, request book already in database
        response = client.get("/books/lookup?q=Cache Test Odyssey")

        #Assertions
        assert response.status_code == 200
        assert response.json()["title"] == "Cache Test Odyssey"

        #Actual Test, verify open librar was never contacted
        mock_search.assert_not_called()
        print("\n✅ PASSED: Data was served purely from PostgreSQL cache!")