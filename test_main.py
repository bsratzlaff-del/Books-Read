#testing main.py
from fastapi.testclient import TestClient
from fastapi import status
from main import app, book_names_db

client = TestClient(app)

def test_delete_book_success():
    book_names_db[1]= "The Great Gatsby"
    response = client.delete("/books/1")

    #assert verifies the 204 return and book is deleted
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert 1 not in book_names_db

def test_delete_book_not_found():
    if 999 in book_names_db:
        del book_names_db[999]

    response = client.delete("/books/999")

    #assert verifies the 404 returns and correct error displays
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Book not found"}

