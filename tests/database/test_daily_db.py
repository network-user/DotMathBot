"""Tests for Daily Challenge persistence layer."""
from __future__ import annotations

import asyncio
from datetime import date, timedelta

import pytest

from app.database.db import (
    complete_daily_attempt,
    get_daily_leaderboard,
    get_or_create_daily_attempt,
    get_or_create_daily_challenge,
    get_or_create_user,
    has_user_done_daily,
    init_db,
)


@pytest.fixture
async def db():
    await init_db()
    yield


# Bump the base date forward enough that concurrent test runs don't collide
# on a row in the daily_challenges table (its challenge_date is UNIQUE).
_DAY_OFFSET = 0


def _fresh_date() -> date:
    """Return a unique date per call so tests don't share challenge rows."""
    global _DAY_OFFSET
    _DAY_OFFSET += 1
    return date(2099, 1, 1) + timedelta(days=_DAY_OFFSET)


def _dummy_specs(seed: int) -> list[dict]:
    return [
        {
            "first_num": seed % 10 + i,
            "second_num": (seed >> i) % 10 + 1,
            "operation": "+",
            "answer": 0,
            "formatted_text": "x+y",
            "metadata": {},
        }
        for i in range(10)
    ]


def _dummy_seed(d: date) -> int:
    return d.toordinal()


@pytest.mark.asyncio
async def test_get_or_create_daily_challenge_creates_first_time(db):
    d = _fresh_date()
    challenge = await get_or_create_daily_challenge(d, _dummy_specs, _dummy_seed)
    assert challenge.challenge_date == d
    assert challenge.seed == _dummy_seed(d)
    assert len(challenge.problem_specs) == 10


@pytest.mark.asyncio
async def test_get_or_create_daily_challenge_idempotent(db):
    d = _fresh_date()
    c1 = await get_or_create_daily_challenge(d, _dummy_specs, _dummy_seed)
    c2 = await get_or_create_daily_challenge(d, _dummy_specs, _dummy_seed)
    assert c1.id == c2.id


@pytest.mark.asyncio
async def test_get_or_create_daily_challenge_race_is_safe(db):
    d = _fresh_date()
    results = await asyncio.gather(
        get_or_create_daily_challenge(d, _dummy_specs, _dummy_seed),
        get_or_create_daily_challenge(d, _dummy_specs, _dummy_seed),
        get_or_create_daily_challenge(d, _dummy_specs, _dummy_seed),
    )
    ids = {c.id for c in results}
    assert len(ids) == 1  # all three resolved to the same row


@pytest.mark.asyncio
async def test_get_or_create_daily_attempt_first_creates(db):
    d = _fresh_date()
    user, _ = await get_or_create_user(telegram_id=20001, username="u", first_name="U")
    attempt, created = await get_or_create_daily_attempt(user.id, d)
    assert created is True
    assert attempt.user_id == user.id
    assert attempt.challenge_date == d
    assert attempt.completed_at is None


@pytest.mark.asyncio
async def test_get_or_create_daily_attempt_second_returns_existing(db):
    d = _fresh_date()
    user, _ = await get_or_create_user(telegram_id=20002, username="u", first_name="U")
    a1, c1 = await get_or_create_daily_attempt(user.id, d)
    a2, c2 = await get_or_create_daily_attempt(user.id, d)
    assert c1 is True and c2 is False
    assert a1.id == a2.id


@pytest.mark.asyncio
async def test_complete_daily_attempt_sets_score_and_timestamp(db):
    d = _fresh_date()
    user, _ = await get_or_create_user(telegram_id=20003, username="u", first_name="U")
    attempt, _ = await get_or_create_daily_attempt(user.id, d)
    await complete_daily_attempt(attempt.id, correct=7, incorrect=3, total_time_ms=42000)
    assert await has_user_done_daily(20003, d) is True


@pytest.mark.asyncio
async def test_has_user_done_daily_false_before_complete(db):
    d = _fresh_date()
    user, _ = await get_or_create_user(telegram_id=20004, username="u", first_name="U")
    await get_or_create_daily_attempt(user.id, d)
    # Attempt row exists but completed_at is NULL → user can still resume.
    assert await has_user_done_daily(20004, d) is False


@pytest.mark.asyncio
async def test_has_user_done_daily_false_for_unknown_user(db):
    assert await has_user_done_daily(99999999, date(2099, 1, 1)) is False


@pytest.mark.asyncio
async def test_get_daily_leaderboard_orders_by_correct_then_time(db):
    d = _fresh_date()
    # Alice: 9 correct, 30s — should outrank Bob (8 correct, 5s)
    alice, _ = await get_or_create_user(telegram_id=21001, username="alice", first_name="A")
    bob, _ = await get_or_create_user(telegram_id=21002, username="bob", first_name="B")
    carol, _ = await get_or_create_user(telegram_id=21003, username="carol", first_name="C")

    a_attempt, _ = await get_or_create_daily_attempt(alice.id, d)
    b_attempt, _ = await get_or_create_daily_attempt(bob.id, d)
    c_attempt, _ = await get_or_create_daily_attempt(carol.id, d)

    await complete_daily_attempt(a_attempt.id, correct=9, incorrect=1, total_time_ms=30000)
    await complete_daily_attempt(b_attempt.id, correct=8, incorrect=2, total_time_ms=5000)
    # Carol ties Alice on correct but is faster → ranks above her.
    await complete_daily_attempt(c_attempt.id, correct=9, incorrect=1, total_time_ms=20000)

    rows, has_next = await get_daily_leaderboard(d, limit=10, offset=0)
    assert has_next is False
    ranked_ids = [u.id for u, _ in rows]
    assert ranked_ids == [carol.id, alice.id, bob.id]


@pytest.mark.asyncio
async def test_get_daily_leaderboard_excludes_incomplete_attempts(db):
    d = _fresh_date()
    user, _ = await get_or_create_user(telegram_id=21010, username="u", first_name="U")
    await get_or_create_daily_attempt(user.id, d)  # no complete_daily_attempt
    rows, _ = await get_daily_leaderboard(d, limit=10, offset=0)
    assert rows == []


@pytest.mark.asyncio
async def test_get_daily_leaderboard_pagination(db):
    d = _fresh_date()
    users = []
    for i in range(5):
        u, _ = await get_or_create_user(
            telegram_id=22000 + i, username=f"u{i}", first_name=f"U{i}"
        )
        users.append(u)
        a, _ = await get_or_create_daily_attempt(u.id, d)
        await complete_daily_attempt(a.id, correct=10 - i, incorrect=i, total_time_ms=1000)

    page1, has_next1 = await get_daily_leaderboard(d, limit=2, offset=0)
    assert len(page1) == 2 and has_next1 is True
    page2, has_next2 = await get_daily_leaderboard(d, limit=2, offset=2)
    assert len(page2) == 2 and has_next2 is True
    page3, has_next3 = await get_daily_leaderboard(d, limit=2, offset=4)
    assert len(page3) == 1 and has_next3 is False
