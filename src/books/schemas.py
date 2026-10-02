from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Book(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_uid: UUID | None = None
    uid: UUID
    title: str = Field(pattern=r"^[^\x00]*$")
    author: str = Field(pattern=r"^[^\x00]*$")
    publisher: str = Field(pattern=r"^[^\x00]*$")
    published_date: date
    page_count: int = Field(ge=-2147483648, le=2147483647)
    language: str = Field(pattern=r"^[^\x00]*$")
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
    title: str = Field(pattern=r"^[^\x00]*$")
    author: str = Field(pattern=r"^[^\x00]*$")
    publisher: str = Field(pattern=r"^[^\x00]*$")
    published_date: date
    page_count: int = Field(ge=-2147483648, le=2147483647)
    language: str = Field(pattern=r"^[^\x00]*$")


class BookUpdateModel(BaseModel):
    title: str = Field(pattern=r"^[^\x00]*$")
    author: str = Field(pattern=r"^[^\x00]*$")
    publisher: str = Field(pattern=r"^[^\x00]*$")
    page_count: int = Field(ge=-2147483648, le=2147483647)
    language: str = Field(pattern=r"^[^\x00]*$")


from src.reviews.schemas import ReviewModel
from src.tags.schemas import TagModel


class BookDetailModel(Book):
    reviews: list[ReviewModel] = []
    tags: list[TagModel] = []
