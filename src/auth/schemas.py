from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6, max_length=72, repr=False)

    @field_validator("password")
    @classmethod
    def validate_bcrypt_password(cls, value: str) -> str:
        # Bcrypt's limit is bytes, so non-ASCII passwords need this check too.
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes")
        if "\x00" in value:
            raise ValueError("Password must not contain null characters")
        return value


class UserModel(BaseModel):
    """Public account response; never expose passwords or stored hashes."""

    model_config = ConfigDict(from_attributes=True)

    uid: UUID
    username: str
    first_name: str | None
    last_name: str | None
    email: str
    role: str = "user"
    is_active: bool = True
    is_verified: bool
    created_at: datetime


class UserLoginModel(BaseModel):
    email: str
    password: str = Field(min_length=6, max_length=72, repr=False)


from src.books.schemas import Book


class UserBooksModel(UserModel):
    books: list[Book] = []
