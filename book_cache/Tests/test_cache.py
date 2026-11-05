#test to ensure the code is properly pulling cache first and topping up from Open Library
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from book_cache.main import app
from book_cache.database import SessionLocal
from book_cache import models
from book_cache.open_book import BookResponse as OLBookResponse


client = TestClient(app)

def test_cache_hit():
    """When the database cache has 5 matching books, Open Library is never contacted."""
    db = SessionLocal()
    test_isbns = [f"999-CACHE-FULL-{i}" for i in range(1, 6)]

    #clean up test from previous runs
    db.query(models.Book_Name).filter(
        (models.Book_Name.isbn.in_(test_isbns)) |
        (models.Book_Name.title.ilike("%Cache Test Odyssey%"))
    ).delete(synchronize_session=False)
    db.commit()

    for i, isbn in enumerate(test_isbns, 1):
        db.add(models.Book_Name(
            title=f"Cache Test Odyssey Vol {i}",
            isbn=isbn,
            author_name="Test Author"
        ))
    db.commit()
    db.close()

    #Second, mock open_book.search_books to track whether or not it gets called
    with patch("book_cache.routes.open_book.search_books", new_callable=AsyncMock) as mock_search:
        #Third, request book already in database
        response = client.get("/books/lookup?q=Cache Test Odyssey")

        #Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert data[0]["title"] == "Cache Test Odyssey Vol 1"

        #Actual Test, verify open library was never contacted because cache fulfilled 5 books
        mock_search.assert_not_called()
        print("\n✅ PASSED: Data was served purely from PostgreSQL cache!")


def test_cache_partial_hit_tops_up():
    """When the cache has fewer than 5 books, it pulls from Open Library to total 5."""
    db = SessionLocal()
    test_isbn = "999-CACHE-PARTIAL"

    #clean up test from previous runs
    db.query(models.Book_Name).filter(models.Book_Name.isbn == test_isbn).delete()
    db.commit()

    db.add(models.Book_Name(
        title="Cache Partial Odyssey",
        isbn=test_isbn,
        author_name="Partial Cache Author"
    ))
    db.commit()
    db.close()

    mock_ol_books = [
        OLBookResponse(title=f"Open Lib Odyssey {i}", isbn=f"OL-999-{i}", author_name=[f"OL Author {i}"])
        for i in range(2, 6)
    ]

    with patch("book_cache.routes.open_book.search_books", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_ol_books

        response = client.get("/books/lookup?q=Cache Partial Odyssey")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        # 1st book is from DB cache (has id)
        assert data[0]["title"] == "Cache Partial Odyssey"
        assert data[0]["id"] is not None

        # 2nd through 5th books are from Open Library (id is None)
        for idx in range(1, 5):
            assert data[idx]["id"] is None
            assert data[idx]["title"] == f"Open Lib Odyssey {idx + 1}"

        # Verify Open Library WAS contacted to top up
        assert mock_search.call_args.kwargs["q"] == "Cache Partial Odyssey"
        assert mock_search.call_args.kwargs["offset"] == 0
        print("\n✅ PASSED: Partial cache hit topped up from Open Library to reach 5 total results!")


def test_cache_pagination_page_two():
    """Verify requesting page 2 calculates correct offsets and returns next set of results."""
    mock_ol_books = [
        OLBookResponse(title=f"Page Two Book {i}", isbn=f"OL-P2-{i}", author_name=[f"Author {i}"])
        for i in range(1, 6)
    ]

    with patch("book_cache.routes.open_book.search_books", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_ol_books

        response = client.get("/books/lookup?q=NonexistentQueryForPagination&page=2&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert data[0]["title"] == "Page Two Book 1"

        # For page 2 with 0 cached books: ol_offset = (2 - 1) * 5 - 0 = 5
        assert mock_search.call_args.kwargs["offset"] == 5
        print("\n✅ PASSED: Page 2 correctly requested Open Library starting from offset 5!")