from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from src.auth.email_routes import router as email_router
from src.auth.routes import auth_router
from src.books.routes import book_router
from src.config import Config
from src.db.main import engine
from src.errors import register_error_handlers
from src.middleware import register_middleware


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

from src.reviews.routes import review_router
from src.tags.routes import tags_router

app.include_router(review_router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(tags_router, prefix="/api/v1/tags", tags=["tags"])

register_error_handlers(app)

register_middleware(app, Config)

app.include_router(email_router, prefix="/api/v1/auth", tags=["auth"])
