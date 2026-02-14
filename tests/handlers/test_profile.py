"""Tests for app.handlers.profile."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.handlers.profile import (
    show_profile_handler,
    show_leaderboard_handler,
    show_tips_handler,
    tips_multiplication_handler,
)


@pytest.fixture
def callback():
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = 12345
    cb.message = MagicMock()
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.mark.asyncio
async def test_show_profile_handler(callback):
    with patch("app.handlers.profile.get_user_language", new_callable=AsyncMock, return_value="ru"), \
         patch("app.handlers.profile.StatsService.get_formatted_profile", new_callable=AsyncMock, return_value="📊 Профиль"):
        await show_profile_handler(callback)
    callback.message.edit_text.assert_called_once()
    assert callback.message.edit_text.call_args[0][0] == "📊 Профиль"
    assert callback.message.edit_text.call_args[1]["parse_mode"] == "Markdown"
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_show_leaderboard_handler(callback):
    with patch("app.handlers.profile.get_user_language", new_callable=AsyncMock, return_value="ru"), \
         patch("app.handlers.profile.StatsService.get_formatted_leaderboard", new_callable=AsyncMock, return_value="🏆 Топ"):
        await show_leaderboard_handler(callback)
    callback.message.edit_text.assert_called_once()
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_show_tips_handler(callback):
    with patch("app.handlers.profile.get_user_language", new_callable=AsyncMock, return_value="ru"):
        await show_tips_handler(callback)
    callback.message.edit_text.assert_called_once()
    assert "совет" in callback.message.edit_text.call_args[0][0].lower() or "tip" in callback.message.edit_text.call_args[0][0].lower()
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_tips_multiplication_handler(callback):
    with patch("app.handlers.profile.get_user_language", new_callable=AsyncMock, return_value="ru"):
        await tips_multiplication_handler(callback)
    callback.message.edit_text.assert_called_once()
    callback.answer.assert_called_once()
