"""Tests for app.handlers.training."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.handlers.training import (
    start_training_handler,
    select_difficulty_handler,
    abort_training_handler,
    kb_after_answer,
)
from app.handlers.training import TrainingStates


@pytest.fixture
def callback():
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = 12345
    cb.message = MagicMock()
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.fixture
def state():
    s = MagicMock()
    s.set_state = AsyncMock()
    s.update_data = AsyncMock()
    s.get_data = AsyncMock(return_value={})
    s.clear = AsyncMock()
    return s


@pytest.mark.asyncio
async def test_start_training_handler(callback, state):
    callback.data = "start_training"
    with patch("app.handlers.training.get_user_language", new_callable=AsyncMock, return_value="ru"):
        await start_training_handler(callback, state)
    state.update_data.assert_called()
    state.set_state.assert_called_with(TrainingStates.waiting_for_difficulty)
    callback.message.edit_text.assert_called_once()
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_select_difficulty_handler(callback, state):
    callback.data = "difficulty_easy"
    state.get_data = AsyncMock(return_value={})
    with patch("app.handlers.training.safe_edit_text", new_callable=AsyncMock):
        await select_difficulty_handler(callback, state)
    state.update_data.assert_called()
    state.set_state.assert_called_with(TrainingStates.waiting_for_mode)
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_abort_training_handler(callback, state):
    callback.data = "abort_training"
    with patch("app.handlers.training.get_user_language", new_callable=AsyncMock, return_value="ru"), \
         patch("app.handlers.training.safe_edit_text", new_callable=AsyncMock):
        await abort_training_handler(callback, state)
    state.clear.assert_called_once()
    callback.answer.assert_called_once()


def test_kb_after_answer_has_next():
    kb = kb_after_answer(True, "ru")
    assert kb.inline_keyboard
    assert len(kb.inline_keyboard) == 2


def test_kb_after_answer_no_next():
    kb = kb_after_answer(False, "en")
    assert kb.inline_keyboard
    assert len(kb.inline_keyboard) >= 1
