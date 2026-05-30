"""Tests for the Quick Start shortcut in training.py."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.handlers.training import TrainingStates, quick_start_handler
from app.keyboards.callbacks import MenuCB


@pytest.fixture
def callback():
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = 99
    cb.message = MagicMock()
    cb.message.chat = MagicMock()
    cb.message.chat.id = 1
    cb.message.message_id = 7
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.fixture
def state():
    s = MagicMock()
    s.clear = AsyncMock()
    s.set_state = AsyncMock()
    s.update_data = AsyncMock()
    s.get_data = AsyncMock(return_value={"lang": "ru"})
    return s


@pytest.mark.asyncio
async def test_quick_start_falls_back_to_picker_without_favorite(callback, state):
    with patch(
        "app.handlers.training.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.training.get_user_favorite",
        new_callable=AsyncMock,
        return_value=(None, None),
    ):
        await quick_start_handler(callback, MenuCB(action="quick_start"), state)
    state.set_state.assert_called_with(TrainingStates.waiting_for_difficulty)
    callback.message.edit_text.assert_called_once()


@pytest.mark.asyncio
async def test_quick_start_launches_session_with_favorite(callback, state):
    session = MagicMock()
    session.id = 123
    with patch(
        "app.handlers.training.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.training.get_user_favorite",
        new_callable=AsyncMock,
        return_value=("mult", "hard"),
    ), patch(
        "app.handlers.training.ProblemGenerator.generate_problems",
        return_value=[MagicMock(), MagicMock(), MagicMock()],
    ), patch(
        "app.handlers.training.create_training_session",
        new_callable=AsyncMock,
        return_value=session,
    ), patch(
        "app.handlers.training.show_problem", new_callable=AsyncMock
    ) as show:
        await quick_start_handler(callback, MenuCB(action="quick_start"), state)
    show.assert_awaited_once()
    state.update_data.assert_called()
    args, kwargs = state.update_data.call_args
    assert kwargs["mode"] == "mult"
    assert kwargs["difficulty"] == "hard"
    assert kwargs["session_id"] == 123


@pytest.mark.asyncio
async def test_quick_start_defaults_to_medium_when_favorite_difficulty_is_null(
    callback, state
):
    session = MagicMock()
    session.id = 7
    with patch(
        "app.handlers.training.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.training.get_user_favorite",
        new_callable=AsyncMock,
        return_value=("mult", None),
    ), patch(
        "app.handlers.training.ProblemGenerator.generate_problems",
        return_value=[MagicMock(), MagicMock()],
    ), patch(
        "app.handlers.training.create_training_session",
        new_callable=AsyncMock,
        return_value=session,
    ), patch(
        "app.handlers.training.show_problem", new_callable=AsyncMock
    ):
        await quick_start_handler(callback, MenuCB(action="quick_start"), state)
    args, kwargs = state.update_data.call_args
    assert kwargs["difficulty"] == "medium"
