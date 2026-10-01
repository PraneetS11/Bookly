"""Add account roles and activation with safe defaults for existing rows."""

import sqlalchemy as sa
from alembic import op

revision = "b10_roles"
down_revision = "a4bb1f95dc35"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user_accounts",
        sa.Column("role", sa.String(), nullable=False, server_default="user"),
    )
    op.add_column(
        "user_accounts",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade():
    op.drop_column("user_accounts", "is_active")
    op.drop_column("user_accounts", "role")
