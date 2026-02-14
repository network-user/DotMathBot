"""Tests for app.services.stats_service."""
import pytest

from app.database.db import init_db, get_or_create_user, create_training_session, complete_training_session
from app.services.stats_service import StatsService


@pytest.fixture
async def db():
    await init_db()
    yield


@pytest.mark.asyncio
async def test_get_formatted_profile_not_found(db):
    text = await StatsService.get_formatted_profile(99999, "ru")
    assert "Профиль не найден" in text or "not found" in text.lower()

    text_en = await StatsService.get_formatted_profile(99999, "en")
    assert "not found" in text_en.lower() or "Profile" in text_en


@pytest.mark.asyncio
async def test_get_formatted_profile_success(db):
    await get_or_create_user(telegram_id=111, username="u1", first_name="User1")
    text = await StatsService.get_formatted_profile(111, "ru")
    assert "Профиль" in text or "профиль" in text or "Статистика" in text
    assert "0" in text

    text_en = await StatsService.get_formatted_profile(111, "en")
    assert "Profile" in text_en or "Stats" in text_en


@pytest.mark.asyncio
async def test_get_formatted_leaderboard_empty_or_with_users(db):
    # DB may be empty or contain users from other tests (shared in-memory)
    text = await StatsService.get_formatted_leaderboard(10, "ru")
    assert "ТОП" in text or "топ" in text or "дней" in text or "сформирован" in text or "training" in text.lower()

    text_en = await StatsService.get_formatted_leaderboard(10, "en")
    assert "leaderboard" in text_en.lower() or "training" in text_en.lower() or "days" in text_en.lower()


@pytest.mark.asyncio
async def test_get_formatted_leaderboard_with_users(db):
    await get_or_create_user(telegram_id=222, username="u2", first_name="User2")
    session = await create_training_session(222, "easy", "mult", 2)
    await complete_training_session(session.id, 2, 0)
    text = await StatsService.get_formatted_leaderboard(5, "ru")
    assert "User2" in text or "дней" in text or "days" in text
