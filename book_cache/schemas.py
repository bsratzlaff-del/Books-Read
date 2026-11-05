#Defines data shape that the client sends in the HTTP request body

from pydantic import BaseModel, ConfigDict
from typing import Optional


#when creating a book and dont know id yet
class BookCreate(BaseModel):
    title: str
    isbn: str
    author_name:str
    year_publish: Optional[int] = None
    

#when sending book back to client
class BookResponse(BookCreate):
    id: Optional[int] = None

    model_config = ConfigDict (from_attributes = True)


#sending book to user_backend
class UserBooksPayload(BaseModel):
    title: str
    isbn: str
    author: str
    year_publish: Optional[int] = None
