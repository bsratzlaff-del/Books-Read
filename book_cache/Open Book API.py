from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import httpx
from models import Book_Name


#Lifespan event to manage httpx client
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code before yield runs on startup
    app.state.http_client = httpx.AsyncClient(base_url="https://openlibrary.org")
    try:
        yield
    finally:
        # Code after yield / in finally runs on shutdown
        await app.state.http_client.aclose()
        

app = FastAPI(title="BookshelfApp", version="1.0", lifespan=lifespan)


#API Routes to Open Book
@app.get("/search", response_model=List[Book_Name])
async def search_books(q: str = Query(..., description="Search query term")):
    client: httpx.AsyncClient = app.state.http_client
    try:
        response = await client.get("/search.json", params={"q": q, "limit": 10})
        response.raise_for_status()
        
        data = response.json()
        docs = data.get("docs", [])
        
        # Instantiate your schemas from models.py
        return [
            BookSearchResult(
                title=doc.get("title"),
                author_name=doc.get("author_name", []),
                first_publish_year=doc.get("first_publish_year"),
                isbn=doc.get("isbn", [])[:3]
            )
            for doc in docs
        ]
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="External API error")


@app.get("/books/{isbn}", response_model=Book_Name)
async def get_book_by_isbn(isbn: str):
    client: httpx.AsyncClient = app.state.http_client
    try:
        response = await client.get(f"/isbn/{isbn}.json")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Book not found")
            
        response.raise_for_status()
        data = response.json()
        
        # Instantiate your schema from models.py
        return Book_Name(
            title=data.get("title"),
            publish_date=data.get("publish_date"),
            number_of_pages=data.get("number_of_pages"),
            publishers=data.get("publishers", [])
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="External API error")