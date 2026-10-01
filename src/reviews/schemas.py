from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreateModel(BaseModel):
    rating: int = Field(ge=1, le=5)
    review_text: str = Field(min_length=1, max_length=4000)


class ReviewModel(ReviewCreateModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    user_uid: UUID
    book_uid: UUID
    created_at: datetime
    updated_at: datetime
