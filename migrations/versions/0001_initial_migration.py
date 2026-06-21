"""Initial schema for DotMathBot on PostgreSQL.

Four tables, hand-written (do not regenerate from models):

- users               — Telegram users + profile counters + notification config.
- training_sessions   — one row per started training run.
- problems            — individual problems inside a session.
- user_training_days  — pre-aggregated "the user trained on date D" set used
                        for the day-streak leaderboard.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0001_initial_migration"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---- users ----------------------------------------------------------
    # telegram_id is stored as TEXT because the canonical Telegram user id
    # is a 64-bit integer and we don't want clients to ever parse it as a
    # JS number on the web side.
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("total_problems_solved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_answers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("incorrect_answers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_training_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("language", sa.String(), nullable=True, server_default="ru"),
        # Privacy default is "hidden" — explicit opt-in to appear on leaderboards.
        sa.Column("show_in_top", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("notification_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notification_preset", sa.String(), nullable=False, server_default="three_times"),
        # JSON-encoded list[str] of HH:MM times, NULL when preset != "custom".
        sa.Column("custom_notification_times", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("telegram_id", name="uq_users_telegram_id"),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    # ---- training_sessions ---------------------------------------------
    op.create_table(
        "training_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # easy / medium / hard
        sa.Column("difficulty", sa.String(), nullable=False),
        # choose | mult | div | mixed | add | sub | div_rem | pow | sqrt
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("total_problems", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("incorrect", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_training_sessions_user_id", "training_sessions", ["user_id"])

    # ---- problems -------------------------------------------------------
    # operation: one of +, −, ×, ÷, ÷r, ^, √ (unicode glyphs to match
    # what we render in chat — keep DB strings stable across UI changes).
    op.create_table(
        "problems",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "session_id",
            sa.Integer(),
            sa.ForeignKey("training_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("first_number", sa.Integer(), nullable=False),
        sa.Column("second_number", sa.Integer(), nullable=False),
        sa.Column("operation", sa.String(), nullable=False),
        sa.Column("correct_answer", sa.Integer(), nullable=False),
        sa.Column("user_answer", sa.Integer(), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default=sa.false()),
        # Op-specific extras serialised as JSON: remainder for ÷r,
        # exponent for ^, radicand for √, display_form overrides, etc.
        sa.Column("metadata_json", sa.Text(), nullable=True),
    )
    op.create_index("ix_problems_session_id", "problems", ["session_id"])

    # ---- user_training_days --------------------------------------------
    # Pre-aggregated set of dates on which a user solved ≥1 problem;
    # used by day-streak leaderboard to avoid scanning training_sessions.
    op.create_table(
        "user_training_days",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        # YYYY-MM-DD; stored as TEXT for cheap composite-PK lookup.
        sa.Column("training_day", sa.String(), primary_key=True),
    )


def downgrade() -> None:
    # Drop children before parents — ForeignKey ondelete=CASCADE is for
    # row-level deletes, not schema-level drop order.
    op.drop_table("user_training_days")
    op.drop_index("ix_problems_session_id", table_name="problems")
    op.drop_table("problems")
    op.drop_index("ix_training_sessions_user_id", table_name="training_sessions")
    op.drop_table("training_sessions")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
