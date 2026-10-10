#how to structure table look in postgreSQL

from .database import Base
from sqlalchemy import Column, Integer, String

class Item(Base):
    __tablename__ = "book_id"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    first_author = Column(String, index=False)
    last_author = Column(String, index=True)


