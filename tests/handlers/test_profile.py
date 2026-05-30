"""Tests for app.handlers.profile."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.handlers.profile import (
    show_leaderboard_handler,
    show_profile_handler,
    show_tips_handler,
    tips_multiplication_handler,
)
from app.keyboards.callbacks import MenuCB, TipsCB


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
    with patch(
        "app.handlers.profile.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.profile.StatsService.get_formatted_profile",
        new_callable=AsyncMock,
        return_value="📊 Профиль",
    ), patch(
        "app.handlers.profile.get_user", new_callable=AsyncMock, return_value=None
    ):
        await show_profile_handler(callback, MenuCB(action="profile"))
    callback.message.edit_text.assert_called_once()
    assert callback.message.edit_text.call_args[0][0] == "📊 Профиль"


@pytest.mark.asyncio
async def test_show_leaderboard_handler(callback):
    with patch(
        "app.handlers.profile.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.profile.StatsService.get_leaderboard_choose_mode_text",
        new_callable=AsyncMock,
        return_value="🏆 Топ",
    ):
        await show_leaderboard_handler(callback, MenuCB(action="leaderboard"))
    callback.message.edit_text.assert_called_once()


@pytest.mark.asyncio
async def test_show_tips_handler(callback):
    with patch(
        "app.handlers.profile.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ):
        await show_tips_handler(callback, MenuCB(action="tips"))
    callback.message.edit_text.assert_called_once()


@pytest.mark.asyncio
async def test_tips_multiplication_handler(callback):
    with patch(
        "app.handlers.profile.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ):
        await tips_multiplication_handler(callback, TipsCB(action="multiplication"))
    callback.message.edit_text.assert_called_once()
