# book_cache/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .open_book import router as open_book_router
from .routes import router as book_cache_router # <-- Import your routes

load_dotenv()
cors_origins = os.getenv("CORS_ORIGINS", "").split(",")

# 1. Create DB tables
Base.metadata.create_all(bind=engine)

# 2. Create App & CORS
app = FastAPI(title="Book Cache Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Mount the two routers!
app.include_router(book_cache_router) # Database CRUD & Cache Lookup (/books)
app.include_router(open_book_router)  # Open Library API (/books/search)