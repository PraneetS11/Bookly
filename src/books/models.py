from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import SQLModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
    )

    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )

    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=utc_now,
        ),
    )

    def __repr__(self) -> str:
        return f"<Book {self.title}>"