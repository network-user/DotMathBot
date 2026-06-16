"""Tests for app.handlers.training (unified anchor-message paradigm)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aiogram.types import CallbackQuery

from app.handlers.training import (
    TrainingStates,
    _record_and_advance,
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


# ---------------------------------------------------------------------------
# Fair-retry guards: the in-session feedback must NEVER reveal the correct
# answer on wrong/skipped, otherwise "Retry mistakes" turns into a
# memorisation check.
# ---------------------------------------------------------------------------


def _problem_spec(answer: int = 75) -> dict:
    """Match the FSM-stored shape (dict spec, Redis-safe)."""
    return {
        "first_num": 5,
        "second_num": 15,
        "operation": "×",
        "answer": answer,
        "formatted_text": "5 × 15",
        "metadata": {},
    }


def _fsm_with(answer: int, session_kind: str = "normal"):
    state = MagicMock()
    state.get_data = AsyncMock(
        return_value={
            "lang": "ru",
            "problems": [_problem_spec(answer)],
            "idx": 0,
            "correct": 0,
            "incorrect": 0,
            "session_streak": 0,
            "current_problem_id": None,
            "problem_shown_at": None,
            "session_kind": session_kind,
        }
    )
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    return state


def _spec_callback():
    cb = MagicMock(spec=CallbackQuery)
    cb.from_user = MagicMock()
    cb.from_user.id = 1
    cb.message = MagicMock()
    cb.message.chat = MagicMock(id=1)
    cb.message.message_id = 1
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.mark.asyncio
@pytest.mark.parametrize("session_kind", ["normal", "retry", "daily"])
async def test_wrong_answer_feedback_does_not_reveal_correct_answer(session_kind):
    state = _fsm_with(answer=75, session_kind=session_kind)
    cb = _spec_callback()
    with patch(
        "app.handlers.training.record_problem_answered", new_callable=AsyncMock
    ), patch(
        "app.handlers.training.finish_training", new_callable=AsyncMock
    ) as finish:
        await _record_and_advance(cb, state, user_answer=99, skipped=False)

    finish.assert_awaited_once()
    feedback = finish.call_args.args[2]
    assert feedback is not None
    assert "75" not in feedback, (
        f"Wrong-answer feedback for {session_kind} leaked the correct answer."
    )


def test_problem_spec_roundtrip_preserves_all_fields():
    """specs -> Problem -> specs is the FSM serialisation pivot.

    Every writer calls ``_problems_to_specs`` before ``state.update_data``;
    every reader calls ``_specs_to_problems`` after ``state.get_data``. If
    either direction drops a field, ``show_problem`` renders garbage. This
    test pins both halves.
    """
    from app.handlers.training import _problem_to_spec, _spec_to_problem
    from app.services.problem_generator import Problem

    original = Problem(
        first_num=12,
        second_num=3,
        operation="÷r",
        answer=4,
        formatted_text="12 ÷ 3",
        metadata={"remainder": 0, "extra": "kept"},
    )
    spec = _problem_to_spec(original)
    rebuilt = _spec_to_problem(spec)
    assert rebuilt.first_num == 12
    assert rebuilt.second_num == 3
    assert rebuilt.operation == "÷r"
    assert rebuilt.answer == 4
    assert rebuilt.formatted_text == "12 ÷ 3"
    assert rebuilt.metadata.get("remainder") == 0
    assert rebuilt.metadata.get("extra") == "kept"


@pytest.mark.asyncio
@pytest.mark.parametrize("session_kind", ["normal", "retry", "daily"])
async def test_skipped_feedback_does_not_reveal_correct_answer(session_kind):
    state = _fsm_with(answer=42, session_kind=session_kind)
    cb = _spec_callback()
    with patch(
        "app.handlers.training.record_problem_answered", new_callable=AsyncMock
    ), patch(
        "app.handlers.training.finish_training", new_callable=AsyncMock
    ) as finish:
        await _record_and_advance(cb, state, user_answer=None, skipped=True)

    finish.assert_awaited_once()
    feedback = finish.call_args.args[2]
    assert feedback is not None
    assert "42" not in feedback, (
        f"Skip feedback for {session_kind} leaked the correct answer."
    )
