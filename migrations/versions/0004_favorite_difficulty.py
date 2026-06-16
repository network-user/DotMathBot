"""Add ``users.favorite_difficulty`` for the Quick Start shortcut.

Paired with ``favorite_mode`` from migration 0003 to fully describe the
session that Quick Start launches. NULL means "default to MEDIUM at
runtime" — the column is purely an override.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0004_favorite_difficulty"
down_revision = "0003_favorite_mode"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("favorite_difficulty", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "favorite_difficulty")
