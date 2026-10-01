from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from src.auth.routes import auth_router
from src.books.routes import book_router
from src.config import Config
from src.db.main import engine


@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting...")
    app.state.redis = Redis.from_url(
        Config.REDIS_URL, socket_connect_timeout=2, socket_timeout=2
    )
    try:
        yield
    finally:
        try:
            await app.state.redis.aclose()
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
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
