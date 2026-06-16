"""Tests for StatsService._format_daily_leaderboard."""
from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

import pytest

from app.database.db import (
    complete_daily_attempt,
    get_or_create_daily_attempt,
    get_or_create_user,
    init_db,
    update_user_show_in_top,
)
from app.services.stats_service import StatsService


@pytest.fixture
async def db():
    await init_db()
    yield


_DATE_OFFSET = 0


def _fresh_date() -> date:
    """Unique non-today date per test to avoid cross-test pollution."""
    global _DATE_OFFSET
    _DATE_OFFSET += 1
    return date(2098, 1, 1) + timedelta(days=_DATE_OFFSET)


@pytest.mark.asyncio
async def test_daily_leaderboard_empty(db):
    d = _fresh_date()
    with patch("app.services.stats_service.today_msk", return_value=d):
        text, has_next = await StatsService.get_formatted_leaderboard(
            limit=10, offset=0, lang="ru", mode="daily"
        )
    assert has_next is False
    assert "никто" in text.lower() or "📭" in text


@pytest.mark.asyncio
async def test_daily_leaderboard_empty_en(db):
    d = _fresh_date()
    with patch("app.services.stats_service.today_msk", return_value=d):
        text, _ = await StatsService.get_formatted_leaderboard(
            limit=10, offset=0, lang="en", mode="daily"
        )
    assert "nobody" in text.lower() or "📭" in text


@pytest.mark.asyncio
async def test_daily_leaderboard_orders_correctly_and_shows_names(db):
    d = _fresh_date()
    alice, _ = await get_or_create_user(telegram_id=80001, username="a", first_name="Alice")
    bob, _ = await get_or_create_user(telegram_id=80002, username="b", first_name="Bob")
    await update_user_show_in_top(alice.telegram_id, True)
    await update_user_show_in_top(bob.telegram_id, True)

    a, _ = await get_or_create_daily_attempt(alice.id, d)
    b, _ = await get_or_create_daily_attempt(bob.id, d)
    # Alice: 9 correct in 20s.  Bob: 10 correct in 30s.
    # Sort key is (correct DESC, total_time_ms ASC) → Bob first.
    await complete_daily_attempt(a.id, correct=9, incorrect=1, total_time_ms=20_000)
    await complete_daily_attempt(b.id, correct=10, incorrect=0, total_time_ms=30_000)

    with patch("app.services.stats_service.today_msk", return_value=d):
        text, has_next = await StatsService.get_formatted_leaderboard(
            limit=10, offset=0, lang="ru", mode="daily"
        )
    assert has_next is False
    assert "Bob" in text and "Alice" in text
    # Bob (10 correct) outranks Alice (9 correct).
    assert text.index("Bob") < text.index("Alice")
    assert "10/10" in text
    assert "9/10" in text


@pytest.mark.asyncio
async def test_daily_leaderboard_hides_users_with_show_in_top_false(db):
    d = _fresh_date()
    user, _ = await get_or_create_user(
        telegram_id=80010, username="hidden_one", first_name="Hidden"
    )
    # Default show_in_top is False — no need to update.
    attempt, _ = await get_or_create_daily_attempt(user.id, d)
    await complete_daily_attempt(attempt.id, correct=5, incorrect=5, total_time_ms=10_000)

    with patch("app.services.stats_service.today_msk", return_value=d):
        text, _ = await StatsService.get_formatted_leaderboard(
            limit=10, offset=0, lang="ru", mode="daily"
        )
    assert "Hidden" not in text
    assert "Скрыто" in text


@pytest.mark.asyncio
async def test_daily_leaderboard_pagination_has_next(db):
    d = _fresh_date()
    for i in range(4):
        u, _ = await get_or_create_user(
            telegram_id=80100 + i, username=f"u{i}", first_name=f"U{i}"
        )
        await update_user_show_in_top(u.telegram_id, True)
        a, _ = await get_or_create_daily_attempt(u.id, d)
        await complete_daily_attempt(a.id, correct=10 - i, incorrect=i, total_time_ms=1000)

    with patch("app.services.stats_service.today_msk", return_value=d):
        text1, has_next1 = await StatsService.get_formatted_leaderboard(
            limit=2, offset=0, lang="ru", mode="daily"
        )
        text2, has_next2 = await StatsService.get_formatted_leaderboard(
            limit=2, offset=2, lang="ru", mode="daily"
        )
    assert has_next1 is True
    assert has_next2 is False
    assert "U0" in text1 and "U1" in text1
    assert "U2" in text2 and "U3" in text2


@pytest.mark.asyncio
async def test_daily_leaderboard_excludes_incomplete_attempts(db):
    d = _fresh_date()
    user, _ = await get_or_create_user(
        telegram_id=80020, username="started_not_finished", first_name="SNF"
    )
    await update_user_show_in_top(user.telegram_id, True)
    # Create attempt but never complete it.
    await get_or_create_daily_attempt(user.id, d)

    with patch("app.services.stats_service.today_msk", return_value=d):
        text, _ = await StatsService.get_formatted_leaderboard(
            limit=10, offset=0, lang="ru", mode="daily"
        )
    assert "SNF" not in text
