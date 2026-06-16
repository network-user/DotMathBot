"""Anchor-redesign schema additions.

Three changes feeding the UX overhaul:

- ``problems.shown_at`` / ``answered_at`` — per-problem timing, enables the
  in-session "⏱ 4.2s" footer, average-time stat in profile, and post-session
  review. Nullable so historical rows stay legal after backfill.
- ``daily_challenges`` — one row per calendar day (Europe/Moscow). Holds the
  PRNG seed and the frozen list of 10 problem specs all users see that day.
  Lazily created the first time anyone opens the challenge on day D.
- ``daily_challenge_attempts`` — one row per (user, day). UNIQUE constraint
  enforces single-attempt-per-day; concurrent first-clicks rely on
  ``ON CONFLICT DO NOTHING`` in db.py.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0002_anchor_redesign"
down_revision = "0001_initial_migration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---- problems: per-problem timing ----------------------------------
    op.add_column(
        "problems",
        sa.Column("shown_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "problems",
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ---- daily_challenges ----------------------------------------------
    op.create_table(
        "daily_challenges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("challenge_date", sa.Date(), nullable=False),
        sa.Column("seed", sa.BigInteger(), nullable=False),
        # JSONB list of {first_num, second_num, operation, answer, formatted_text, metadata}
        sa.Column("problem_specs", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("challenge_date", name="uq_daily_challenges_date"),
    )

    # ---- daily_challenge_attempts --------------------------------------
    op.create_table(
        "daily_challenge_attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Plain DATE column (not FK to daily_challenges.challenge_date) so
        # attempts can be inserted before the challenge row exists in race
        # conditions; uniqueness on (user_id, challenge_date) is enough.
        sa.Column("challenge_date", sa.Date(), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("correct", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("incorrect", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_time_ms", sa.BigInteger(), nullable=False, server_default="0"),
        sa.UniqueConstraint(
            "user_id", "challenge_date", name="uq_dca_user_date"
        ),
    )
    op.create_index(
        "ix_dca_date_score",
        "daily_challenge_attempts",
        ["challenge_date", "correct", "total_time_ms"],
    )


def downgrade() -> None:
    op.drop_index("ix_dca_date_score", table_name="daily_challenge_attempts")
    op.drop_table("daily_challenge_attempts")
    op.drop_table("daily_challenges")
    op.drop_column("problems", "answered_at")
    op.drop_column("problems", "shown_at")
