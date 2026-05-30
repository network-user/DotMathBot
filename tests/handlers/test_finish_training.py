"""Tests for finish_training — both normal and daily session_kind branches."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aiogram.types import CallbackQuery

from app.database.db import (
    complete_training_session,  # noqa: F401  (re-exported sanity)
    create_training_session,
    get_or_create_daily_attempt,
    get_or_create_user,
    init_db,
)
from app.database.models import DailyChallengeAttempt
from app.handlers.training import finish_training


@pytest.fixture
async def db():
    await init_db()
    yield


def _make_callback():
    # spec=CallbackQuery so finish_training's isinstance check routes through safe_edit.
    cb = MagicMock(spec=CallbackQuery)
    cb.from_user = MagicMock()
    cb.from_user.id = 70001
    cb.message = MagicMock()
    cb.message.chat = MagicMock()
    cb.message.chat.id = 700
    cb.message.message_id = 7
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    return cb


def _make_state(data: dict):
    s = MagicMock()
    s.get_data = AsyncMock(return_value=data)
    s.update_data = AsyncMock()
    s.set_state = AsyncMock()
    s.clear = AsyncMock()
    return s


@pytest.mark.asyncio
async def test_finish_training_daily_completes_attempt(db):
    user, _ = await get_or_create_user(
        telegram_id=70001, username="daily_finisher", first_name="DF"
    )
    challenge_date = datetime(2099, 6, 1).date()
    attempt, _ = await get_or_create_daily_attempt(user.id, challenge_date)
    session = await create_training_session(
        telegram_id=70001, difficulty="hard", mode="mixed", total_problems=10
    )

    # Pretend the session started 12 seconds ago — finish_training computes
    # total_time_ms as (now - session_started_at).
    session_started = datetime.now(timezone.utc) - timedelta(seconds=12)
    state = _make_state(
        {
            "lang": "ru",
            "session_id": session.id,
            "correct": 7,
            "incorrect": 3,
            "session_kind": "daily",
            "daily_attempt_id": attempt.id,
            "session_started_at": session_started.isoformat(),
            "anchor_chat_id": 700,
            "anchor_message_id": 7,
        }
    )
    callback = _make_callback()

    with patch("app.handlers.training.safe_edit", new_callable=AsyncMock):
        await finish_training(callback, state)

    # Re-read the attempt and check it was completed.
    from sqlalchemy import select
    from app.database.db import async_session_maker

    async with async_session_maker() as s:
        result = await s.execute(
            select(DailyChallengeAttempt).where(DailyChallengeAttempt.id == attempt.id)
        )
        updated = result.scalar_one()

    assert updated.completed_at is not None
    assert updated.correct == 7
    assert updated.incorrect == 3
    # Allow some jitter — the timer just needs to land near 12s.
    assert 8_000 <= updated.total_time_ms <= 30_000


@pytest.mark.asyncio
async def test_finish_training_normal_does_not_touch_daily_attempt(db):
    user, _ = await get_or_create_user(
        telegram_id=70002, username="normal_finisher", first_name="NF"
    )
    challenge_date = datetime(2099, 6, 2).date()
    # Create an attempt that should NOT be touched.
    attempt, _ = await get_or_create_daily_attempt(user.id, challenge_date)
    session = await create_training_session(
        telegram_id=70002, difficulty="easy", mode="add", total_problems=5
    )

    state = _make_state(
        {
            "lang": "ru",
            "session_id": session.id,
            "correct": 4,
            "incorrect": 1,
            "session_kind": "normal",
            "daily_attempt_id": attempt.id,  # present but should be ignored
        }
    )
    callback = _make_callback()
    callback.from_user.id = 70002

    with patch("app.handlers.training.safe_edit", new_callable=AsyncMock):
        await finish_training(callback, state)

    from sqlalchemy import select
    from app.database.db import async_session_maker

    async with async_session_maker() as s:
        result = await s.execute(
            select(DailyChallengeAttempt).where(DailyChallengeAttempt.id == attempt.id)
        )
        untouched = result.scalar_one()

    assert untouched.completed_at is None
    assert untouched.correct == 0
    assert untouched.incorrect == 0


@pytest.mark.asyncio
async def test_finish_training_daily_handles_missing_started_at(db):
    """If session_started_at is absent from FSM, total_time_ms defaults to 0."""
    user, _ = await get_or_create_user(
        telegram_id=70003, username="no_timer", first_name="NT"
    )
    challenge_date = datetime(2099, 6, 3).date()
    attempt, _ = await get_or_create_daily_attempt(user.id, challenge_date)
    session = await create_training_session(
        telegram_id=70003, difficulty="hard", mode="mixed", total_problems=10
    )

    state = _make_state(
        {
            "lang": "ru",
            "session_id": session.id,
            "correct": 10,
            "incorrect": 0,
            "session_kind": "daily",
            "daily_attempt_id": attempt.id,
            # session_started_at deliberately omitted
        }
    )
    callback = _make_callback()
    callback.from_user.id = 70003

    with patch("app.handlers.training.safe_edit", new_callable=AsyncMock):
        await finish_training(callback, state)

    from sqlalchemy import select
    from app.database.db import async_session_maker

    async with async_session_maker() as s:
        result = await s.execute(
            select(DailyChallengeAttempt).where(DailyChallengeAttempt.id == attempt.id)
        )
        updated = result.scalar_one()

    assert updated.completed_at is not None
    assert updated.correct == 10
    assert updated.total_time_ms == 0
