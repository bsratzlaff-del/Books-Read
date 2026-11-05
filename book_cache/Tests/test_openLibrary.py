#tests the Open Library API 
from fastapi.testclient import TestClient
from book_cache.main import app
from book_cache import routes

client = TestClient(app)

def test_open_library_search_success():
    # 1. Query a known book from Open Library
    response = client.get("/books/search?q=Dune")

    # 2. Check HTTP status
    assert response.status_code == 200
    
    # 3. Verify data structure
    results = response.json()
    assert isinstance(results, list)
    assert len(results) > 0

    first_book = results[0]
    assert "title" in first_book
    assert "author_name" in first_book
    assert "isbn" in first_book

    print(f"\n✅ Open Library returned: '{first_book['title']}' by {first_book['author_name']}")

def test_open_library_search_missing_query():
    # Missing query parameter should return 400
    response = client.get("/books/search")
    assert response.status_code == 400
    print("\n✅ Correctly rejected request with missing search query!")

def test_create_and_get_all_books_route():
    test_payload = {
        "title": "Route Test Novel",
        "isbn": "999-ROUTE-TEST",
        "author_name": "Route Author"
    }
    # 1. Test POST /books
    post_res = client.post("/books", json=test_payload)
    assert post_res.status_code in (201, 400) # 201 Created or 400 if already exists
    # 2. Test GET /books
    get_res = client.get("/books")
    assert get_res.status_code == 200
    assert isinstance(get_res.json(), list)
    print("\n✅ Successfully verified CRUD routes on /books!")