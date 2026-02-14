"""Tests for app.handlers.start."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.types import Message, User as TgUser, Chat
from aiogram.fsm.context import FSMContext

from app.handlers.start import (
    start_handler,
    language_switch_handler,
    back_to_menu_handler,
    train_command,
    help_command,
)


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
    s = MagicMock(spec=FSMContext)
    s.clear = AsyncMock()
    return s


@pytest.fixture
def callback():
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = 12345
    cb.message = MagicMock()
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    cb.data = "back_to_menu"
    return cb


@pytest.mark.asyncio
async def test_start_handler_creates_user_and_sends_welcome(message, state):
    with patch("app.handlers.start.get_or_create_user", new_callable=AsyncMock) as m_get:
        user = MagicMock()
        user.language = "ru"
        m_get.return_value = (user, True)
        await start_handler(message, state)
    m_get.assert_called_once_with(telegram_id=12345, username="testuser", first_name="Test")
    message.answer.assert_called_once()
    call_args = message.answer.call_args
    assert "Math Trainer" in call_args[0][0] or "Привет" in call_args[0][0]
    state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_train_command_clears_state_and_sends_difficulty(message, state):
    with patch("app.handlers.start.get_user_language", new_callable=AsyncMock, return_value="ru"):
        await train_command(message, state)
    state.clear.assert_called_once()
    message.answer.assert_called_once()
    assert "сложности" in message.answer.call_args[0][0].lower() or "difficulty" in message.answer.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_help_command_sends_help(message):
    with patch("app.handlers.start.get_user_language", new_callable=AsyncMock, return_value="ru"):
        await help_command(message)
    message.answer.assert_called_once()
    assert "/start" in message.answer.call_args[0][0] or "Помощь" in message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_back_to_menu_edits_message(callback, state):
    with patch("app.handlers.start.get_user_language", new_callable=AsyncMock, return_value="ru"):
        await back_to_menu_handler(callback, state)
    state.clear.assert_called_once()
    callback.message.edit_text.assert_called_once()
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_language_switch_to_en():
    callback = MagicMock()
    callback.from_user = MagicMock()
    callback.from_user.id = 111
    callback.message = MagicMock()
    callback.message.edit_text = AsyncMock()
    callback.answer = AsyncMock()
    callback.data = "lang_en"
    state = MagicMock()

    with patch("app.handlers.start.update_user_language", new_callable=AsyncMock), \
         patch("app.handlers.start.get_user_language", new_callable=AsyncMock, return_value="en"):
        await language_switch_handler(callback, state)
    callback.answer.assert_called_once()
    callback.message.edit_text.assert_called_once()
