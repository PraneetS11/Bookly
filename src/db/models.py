import uuid
from datetime import date, datetime, timezone
from uuid import UUID, uuid4

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "user_accounts"

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            info={"description": "Unique identifier for the user account"},
        ),
    )

    username: str

    first_name: str | None = Field(
        default=None,
        nullable=True,
    )

    last_name: str | None = Field(
        default=None,
        nullable=True,
    )

    is_verified: bool = Field(
        default=False,
        nullable=False,
    )

    email: str

    role: str = Field(
        default="user", sa_column=Column(String, nullable=False, server_default="user")
    )
    is_active: bool = Field(
        default=True, sa_column=Column(Boolean, nullable=False, server_default="true")
    )

    password_hash: str = Field(exclude=True)

    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    books: list["Book"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: list["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"passive_deletes": "all"}
    )


def utc_now():
    return datetime.now(timezone.utc)


class BookTag(SQLModel, table=True):
    book_id: UUID = Field(foreign_key="books.uid", primary_key=True, ondelete="CASCADE")
    tag_id: UUID = Field(foreign_key="tags.uid", primary_key=True, ondelete="CASCADE")


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

    user_uid: UUID | None = Field(
        default=None, foreign_key="user_accounts.uid", ondelete="SET NULL"
    )
    user: User | None = Relationship(back_populates="books")
    reviews: list["Review"] = Relationship(
        back_populates="book",
        sa_relationship_kwargs={"lazy": "selectin", "passive_deletes": "all"},
    )
    tags: list["Tag"] = Relationship(
        back_populates="books",
        link_model=BookTag,
        sa_relationship_kwargs={"lazy": "selectin", "passive_deletes": True},
    )

    title: str
    author: str
    publisher: str
    published_date: date = Field(sa_column=Column(Date, nullable=False))
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


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="review_rating_range"),
    )
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    rating: int
    review_text: str
    user_uid: UUID = Field(foreign_key="user_accounts.uid", ondelete="CASCADE")
    book_uid: UUID = Field(foreign_key="books.uid", ondelete="CASCADE")
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=utc_now),
    )
    user: User = Relationship(back_populates="reviews")
    book: Book = Relationship(back_populates="reviews")


class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    books: list[Book] = Relationship(
        back_populates="tags",
        link_model=BookTag,
        sa_relationship_kwargs={"passive_deletes": True},
    )
