import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query
import httpx
from pydantic import BaseModel

load_dotenv()
CONTACT_EMAIL = os.getenv("APP_CONTACT_EMAIL", "default@example.com")

router = APIRouter(prefix="/books", tags=["Books"])


class BookResponse(BaseModel):
    title: Optional[str] = None
    author_name: Optional[List[str]] = []
    first_publish_year: Optional[int] = None
    isbn: Optional[str] = None


@router.get("/search", response_model=List[BookResponse])
async def search_books(
    q: Optional[str] = Query(None, description="Search query"),
    title: Optional[str] = Query(None, description="Book title"),
):
    query_term = title or q
    if not query_term:
        raise HTTPException(
            status_code=400,
            detail="Must provide either 'title' or 'q' query parameter",
        )

    headers = {"User-Agent": f"BookshelfApp/1.0 (contact: {CONTACT_EMAIL})"}

    # Explicitly asking Open Library to return isbn and edition_key
    params = {
        "q": query_term,
        "limit": 5,
        "fields": "title,author_name,first_publish_year,isbn,edition_key",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                "https://openlibrary.org/search.json",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Open Library error: {exc.response.text}",
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Unable to reach Open Library: {str(exc)}",
            )

    data = response.json()
    docs = data.get("docs", [])

    results = []
    for doc in docs:
        isbns = doc.get("isbn", [])
        primary_isbn = isbns[0] if isbns else None

        results.append(
            BookResponse(
                title=doc.get("title"),
                author_name=doc.get("author_name", []),
                first_publish_year=doc.get("first_publish_year"),
                isbn=primary_isbn,
            )
        )

    return results