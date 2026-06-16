"""Tests for the post-session "Retry mistakes" flow."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.database.db import (
    create_training_session,
    get_or_create_user,
    get_session_mistakes,
    init_db,
    record_problem_answered,
    record_problem_shown,
)
from app.keyboards.inline import InlineKeyboards


@pytest.fixture
async def db():
    await init_db()
    yield


@pytest.mark.asyncio
async def test_get_session_mistakes_count_matches(db):
    await get_or_create_user(telegram_id=30001, username="r1", first_name="R")
    session = await create_training_session(30001, "easy", "add", total_problems=3)

    pid_ok = await record_problem_shown(session.id, 1, 1, "+", 2)
    pid_bad1 = await record_problem_shown(session.id, 2, 2, "+", 4)
    pid_bad2 = await record_problem_shown(session.id, 3, 3, "+", 6)

    await record_problem_answered(pid_ok, user_answer=2, is_correct=True)
    await record_problem_answered(pid_bad1, user_answer=5, is_correct=False)
    await record_problem_answered(pid_bad2, user_answer=7, is_correct=False)

    mistakes = await get_session_mistakes(session.id)
    assert len(mistakes) == 2
    assert {m.id for m in mistakes} == {pid_bad1, pid_bad2}


def test_result_keyboard_hides_retry_when_no_mistakes():
    kb = InlineKeyboards.session_result(has_mistakes=False, lang="ru", session_kind="normal")
    flat = [b for row in kb.inline_keyboard for b in row]
    texts = [b.text for b in flat]
    assert not any("Перерешать" in t or "Retry" in t for t in texts)


def test_result_keyboard_shows_retry_when_mistakes():
    kb = InlineKeyboards.session_result(has_mistakes=True, lang="ru", session_kind="normal")
    flat = [b for row in kb.inline_keyboard for b in row]
    texts = [b.text for b in flat]
    assert any("Перерешать" in t for t in texts)
