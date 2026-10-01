from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.models import Book  # noqa: F401 - register the table before create_all
from src.config import Config

engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True,
    connect_args={
        "ssl": "require",
        # Avoid stale prepared statements through the development DB pooler.
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
)


SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with SessionLocal() as session:
        yield session
