from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.books.routes import book_router
from src.db.main import engine, init_db


@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting...")
    try:
        await init_db()
        yield
    finally:
        await engine.dispose()
        print("server has been stopped")


version = "v1"

app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version=version,
    lifespan=life_span,
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
