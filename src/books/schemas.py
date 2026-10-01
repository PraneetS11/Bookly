from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Book(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_uid: UUID | None = None
    uid: UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime


class BookCreateModel(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Fictional Field Guide",
                    "author": "Demo Author",
                    "publisher": "Demo Press",
                    "published_date": "2024-01-01",
                    "page_count": 100,
                    "language": "English",
                }
            ]
        }
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str


class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str


from src.reviews.schemas import ReviewModel
from src.tags.schemas import TagModel


class BookDetailModel(Book):
    reviews: list[ReviewModel] = []
    tags: list[TagModel] = []
