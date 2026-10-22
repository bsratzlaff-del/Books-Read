#how to structure table look in postgreSQL
from .database import Base
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel

class Book_Name(Base):
    __tablename__ = "book_id"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    author_name = Column(String, index=False)
    

#To import from Open Library to app. then will pull all info
class BookResponse(BaseModel):
    id: int | None = None
    title: str
    isbn: str
    author_name: str | None = None

    class Config:
        from_attributes = True