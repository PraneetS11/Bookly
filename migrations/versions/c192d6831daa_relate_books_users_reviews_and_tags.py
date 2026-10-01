"""relate books users reviews and tags

Revision ID: c192d6831daa
Revises: b10_roles
Create Date: 2026-10-01 13:25:27.215886

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "c192d6831daa"
down_revision: Union[str, Sequence[str], None] = "b10_roles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tags",
        sa.Column("uid", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("uid"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "booktag",
        sa.Column("book_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.uid"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.uid"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("book_id", "tag_id"),
    )
    op.create_table(
        "reviews",
        sa.Column("uid", sa.Uuid(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("review_text", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_uid", sa.Uuid(), nullable=False),
        sa.Column("book_uid", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="review_rating_range"),
        sa.ForeignKeyConstraint(["book_uid"], ["books.uid"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["user_uid"], ["user_accounts.uid"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("uid"),
    )
    op.add_column("books", sa.Column("user_uid", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "books_user_uid_fkey",
        "books",
        "user_accounts",
        ["user_uid"],
        ["uid"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("books_user_uid_fkey", "books", type_="foreignkey")
    op.drop_column("books", "user_uid")
    op.drop_table("reviews")
    op.drop_table("booktag")
    op.drop_table("tags")
