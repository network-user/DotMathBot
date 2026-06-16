"""Tests for per-problem persistence (Problem.shown_at/answered_at)."""
from __future__ import annotations

import asyncio
import pytest

from app.database.db import (
    create_training_session,
    get_avg_problem_time,
    get_or_create_user,
    get_session_mistakes,
    init_db,
    record_problem_answered,
    record_problem_shown,
)


@pytest.fixture
async def db():
    await init_db()
    yield


async def _make_session(telegram_id: int) -> int:
    await get_or_create_user(telegram_id=telegram_id, username="t", first_name="T")
    s = await create_training_session(
        telegram_id=telegram_id, difficulty="easy", mode="add", total_problems=3
    )
    return s.id


@pytest.mark.asyncio
async def test_record_problem_shown_returns_id_and_sets_timing(db):
    sid = await _make_session(10001)
    pid = await record_problem_shown(
        session_id=sid,
        first_number=12,
        second_number=8,
        operation="+",
        correct_answer=20,
    )
    assert isinstance(pid, int) and pid > 0

    mistakes = await get_session_mistakes(sid)
    # is_correct defaults to False, so an unanswered problem is "incorrect" —
    # this matters: get_session_mistakes is meant for completed sessions only.
    assert any(m.id == pid for m in mistakes)


@pytest.mark.asyncio
async def test_record_problem_answered_updates_correctness(db):
    sid = await _make_session(10002)
    pid = await record_problem_shown(
        session_id=sid, first_number=5, second_number=5, operation="+", correct_answer=10
    )
    await record_problem_answered(pid, user_answer=10, is_correct=True)

    mistakes = await get_session_mistakes(sid)
    assert all(m.id != pid for m in mistakes)


@pytest.mark.asyncio
async def test_get_session_mistakes_returns_only_incorrect(db):
    sid = await _make_session(10003)
    p1 = await record_problem_shown(sid, 1, 1, "+", 2)
    p2 = await record_problem_shown(sid, 2, 2, "+", 4)
    p3 = await record_problem_shown(sid, 3, 3, "+", 6)
    await record_problem_answered(p1, user_answer=2, is_correct=True)
    await record_problem_answered(p2, user_answer=5, is_correct=False)
    await record_problem_answered(p3, user_answer=7, is_correct=False)

    mistakes = await get_session_mistakes(sid)
    mistake_ids = {m.id for m in mistakes}
    assert mistake_ids == {p2, p3}


@pytest.mark.asyncio
async def test_get_session_mistakes_empty_for_perfect_session(db):
    sid = await _make_session(10004)
    p1 = await record_problem_shown(sid, 1, 1, "+", 2)
    await record_problem_answered(p1, user_answer=2, is_correct=True)
    assert await get_session_mistakes(sid) == []


@pytest.mark.asyncio
async def test_get_avg_problem_time_none_when_no_data(db):
    await get_or_create_user(telegram_id=10005, username="t", first_name="T")
    assert await get_avg_problem_time(10005) is None


@pytest.mark.asyncio
async def test_get_avg_problem_time_returns_average(db):
    sid = await _make_session(10006)
    p1 = await record_problem_shown(sid, 1, 1, "+", 2)
    # Wait a measurable interval so answered_at - shown_at > 0.
    await asyncio.sleep(0.05)
    await record_problem_answered(p1, user_answer=2, is_correct=True)
    avg = await get_avg_problem_time(10006)
    assert avg is not None
    assert avg >= 0.04  # ≈ 0.05s give or take scheduler jitter


@pytest.mark.asyncio
async def test_get_avg_problem_time_unknown_user(db):
    assert await get_avg_problem_time(99999999) is None
