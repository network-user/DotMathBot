"""Tests for app.handlers.training (unified anchor-message paradigm)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.handlers.training import (
    TrainingStates,
    abort_training_handler,
    select_difficulty_handler,
    start_training_handler,
)
from app.keyboards.callbacks import MenuCB, TrainingCB


@pytest.fixture
def callback():
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = 12345
    cb.message = MagicMock()
    cb.message.chat = MagicMock()
    cb.message.chat.id = 9876
    cb.message.message_id = 1
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.fixture
def state():
    s = MagicMock()
    s.set_state = AsyncMock()
    s.update_data = AsyncMock()
    s.get_data = AsyncMock(return_value={"lang": "ru"})
    s.clear = AsyncMock()
    return s


@pytest.mark.asyncio
async def test_start_training_handler_sets_difficulty_state(callback, state):
    cb_data = MenuCB(action="training")
    with patch(
        "app.handlers.training.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ):
        await start_training_handler(callback, cb_data, state)
    state.clear.assert_called_once()
    state.update_data.assert_called()
    state.set_state.assert_called_with(TrainingStates.waiting_for_difficulty)
    callback.message.edit_text.assert_called_once()
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_select_difficulty_handler_advances_to_mode(callback, state):
    cb_data = TrainingCB(action="difficulty", difficulty="easy")
    state.get_data = AsyncMock(return_value={"lang": "ru"})
    await select_difficulty_handler(callback, cb_data, state)
    state.update_data.assert_called()
    state.set_state.assert_called_with(TrainingStates.waiting_for_mode)
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_abort_training_handler_clears_state(callback, state):
    cb_data = TrainingCB(action="exit")
    with patch(
        "app.handlers.training.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ):
        await abort_training_handler(callback, cb_data, state)
    state.clear.assert_called_once()
    callback.message.edit_text.assert_called_once()
    callback.answer.assert_called_once()
