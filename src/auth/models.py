from datetime import datetime
import uuid

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Column, func
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "user_accounts"

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            info={
                "description": "Unique identifier for the user account"
            },
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

    password_hash: str

    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"
