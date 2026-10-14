from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

OPEN_LIBRARY_HEADERS = {
    "User-Agent": "BookshelfApp/1.0 (bsratzlaff@gmail.com)"
}

@router.get("/books/lookup")