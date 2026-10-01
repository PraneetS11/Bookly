from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TagCreateModel(BaseModel):
    name: str = Field(min_length=1, max_length=80, pattern=r".*\S.*")


class TagModel(TagCreateModel):
    model_config = ConfigDict(from_attributes=True)
    uid: UUID
    created_at: datetime


class TagAddModel(BaseModel):
    tags: list[TagCreateModel] = Field(min_length=1, max_length=30)
