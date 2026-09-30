from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from src.config import Config


engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True,
    connect_args={
        "ssl": "require",
    },
)


async def init_db():
    async with engine.begin() as conn:
        # Import models before create_all so SQLModel knows the tables exist.
        from src.books.models import Book

        await conn.run_sync(SQLModel.metadata.create_all)