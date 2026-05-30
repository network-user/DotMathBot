"""Add ``users.favorite_mode`` for the Quick Start shortcut.

The main menu shows a "⚡ Quick start" row that launches a session in the
user's preferred mode without going through the difficulty/mode pickers.
The column is nullable: a NULL value means "no favorite" and Quick Start
isn't rendered.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0003_favorite_mode"
down_revision = "0002_anchor_redesign"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("favorite_mode", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "favorite_mode")
