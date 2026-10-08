#Defines data shape that the client sends in the HTTP request body

from pydantic import BaseModel

#when creating a book and dont know id yet
class BookCreate(BaseModel):
    title: str
    isbn: str
    first_author:str
    last_author: str

#when sending book back to client
class BookResponse(BookCreate):
    id: int

    class Config:
        from_attributes = True