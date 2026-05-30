"""Tests for app.handlers.start (factory-based filters)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aiogram.types import Message, User as TgUser

from app.handlers.start import (
    back_to_menu_handler,
    help_command,
    language_switch_handler,
    start_handler,
    train_command,
)
from app.keyboards.callbacks import BackCB, MenuCB


@pytest.fixture
def message():
    msg = MagicMock(spec=Message)
    msg.from_user = MagicMock(spec=TgUser)
    msg.from_user.id = 12345
    msg.from_user.username = "testuser"
    msg.from_user.first_name = "Test"
    msg.answer = AsyncMock()
    return msg


@pytest.fixture
def state():
    s = MagicMock()
    s.clear = AsyncMock()
    s.set_state = AsyncMock()
    s.update_data = AsyncMock()
    s.get_data = AsyncMock(return_value={})
    return s


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
async def test_start_handler_creates_user_and_sends_welcome(message, state):
    user = MagicMock()
    user.language = "ru"
    with patch(
        "app.handlers.start.get_or_create_user",
        new_callable=AsyncMock,
        return_value=(user, True),
    ), patch(
        "app.handlers.start.has_user_done_daily",
        new_callable=AsyncMock,
        return_value=False,
    ):
        await start_handler(message, state)
    assert message.answer.call_count == 2
    welcome_text = message.answer.call_args_list[0][0][0]
    assert "Math Trainer" in welcome_text or "Привет" in welcome_text
    state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_train_command_clears_state_and_sends_difficulty(message, state):
    with patch(
        "app.handlers.start.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ):
        await train_command(message, state)
    state.clear.assert_called_once()
    message.answer.assert_called_once()
    sent = message.answer.call_args[0][0]
    assert "сложн" in sent.lower() or "difficult" in sent.lower() or "🎓" in sent


@pytest.mark.asyncio
async def test_help_command_sends_help(message):
    with patch(
        "app.handlers.start.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ):
        await help_command(message)
    assert message.answer.call_count >= 1
    help_text = message.answer.call_args_list[0][0][0]
    assert "/start" in help_text or "Помощь" in help_text


@pytest.mark.asyncio
async def test_back_to_menu_edits_message_once(callback, state):
    state.get_data = AsyncMock(return_value={})
    with patch(
        "app.handlers.start.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.start.has_user_done_daily",
        new_callable=AsyncMock,
        return_value=False,
    ):
        await back_to_menu_handler(callback, BackCB(action="menu"), state)
    state.clear.assert_called_once()
    callback.message.edit_text.assert_called_once()
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_language_switch_to_en(state):
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = 111
    cb.message = MagicMock()
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    with patch(
        "app.handlers.start.update_user_language", new_callable=AsyncMock
    ), patch(
        "app.handlers.start.has_user_done_daily",
        new_callable=AsyncMock,
        return_value=False,
    ):
        await language_switch_handler(cb, MenuCB(action="lang_en"), state)
    cb.answer.assert_called_once()
    cb.message.edit_text.assert_called_once()
