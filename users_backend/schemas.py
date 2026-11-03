from pydantic import BaseModel
from typing import Optional

from fastapi import FastAPI
from schemas import BookRecieveSchema

#importing from book_cache/schemas.py
class UserBooksPayload(BaseModel):
    title: str
    isbn: str
    author: str
    year_publish: Optional[int] = None

#connects from main.py to this backend

