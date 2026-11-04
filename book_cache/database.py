from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

import os
from dotenv import load_dotenv

#to make database url go to .env file for easy conversion and security
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

#Manages the actual network connection pool to PostgreSQL
engine = create_engine(DATABASE_URL)

#Factory for generating fresh database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#base class that data models/tables will inherit from 
Base = declarative_base()

#yields database session
def get_db_books():
    db_books = SessionLocal()
    try:
        yield db_books
    finally:
        db_books.close()







#\connection test for terminal
from sqlalchemy import text

if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1;"))
            print("\n✅ Database connected successfully! Result:", result.scalar())
    except Exception as e:
        print("\n❌ Connection failed:")
        print(e)
#