"""Unified training flow: one anchor message edited in place for every turn.

The previous implementation had two parallel paradigms (choose-answer used
``message.answer`` per turn, picker-answer used ``edit_text``); this module
collapses them into one function pair (``show_problem``/``finish_training``)
that takes a ``session_kind`` discriminator to branch session-level decisions
(retry vs daily vs normal). The typed-answer mode now deletes the user's
reply and edits the same anchor message, so the chat never piles up.

Per-problem Problem rows are persisted (shown_at on render, answered_at on
answer) — required for "Retry mistakes" and timing stats.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.database.db import (
    complete_daily_attempt,
    complete_training_session,
    create_training_session,
    get_session_mistakes,
    get_user_favorite,
    get_user_language,
    record_problem_answered,
    record_problem_shown,
)
from app.keyboards.callbacks import TrainingCB
from app.keyboards.inline import InlineKeyboards
from app.locales import get_text
from app.services.problem_generator import Problem, ProblemGenerator
from app.utils.constants import DIFFICULTY_CONFIG, Difficulty, TrainingMode
from app.utils.ui import (
    delete_user_message,
    edit_anchor,
    format_problem_anchor,
    format_session_result,
    safe_edit,
)

router = Router()
logger = logging.getLogger(__name__)


class TrainingStates(StatesGroup):
    waiting_for_difficulty = State()
    waiting_for_mode = State()
    waiting_for_answer = State()
    viewing_results = State()


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


@router.callback_query(
    TrainingCB.filter(F.action == "difficulty"), TrainingStates.waiting_for_difficulty
)
async def select_difficulty_handler(
    callback: CallbackQuery, callback_data: TrainingCB, state: FSMContext
) -> None:
    await state.update_data(difficulty=callback_data.difficulty)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await state.set_state(TrainingStates.waiting_for_mode)
    await safe_edit(
        callback,
        get_text("choose_mode", lang),
        InlineKeyboards.mode_selection(lang),
    )
    await callback.answer()


@router.callback_query(
    TrainingCB.filter(F.action.in_({"mode_more", "mode_less"})),
    TrainingStates.waiting_for_mode,
)
async def toggle_mode_expansion_handler(
    callback: CallbackQuery, callback_data: TrainingCB, state: FSMContext
) -> None:
    """Expand/collapse the mode picker without losing the chosen difficulty."""
    data = await state.get_data()
    lang = data.get("lang", "ru")
    expanded = callback_data.action == "mode_more"
    await safe_edit(
        callback,
        get_text("choose_mode", lang),
        InlineKeyboards.mode_selection(lang, expanded=expanded),
    )
    await callback.answer()


@router.callback_query(
    TrainingCB.filter(F.action == "mode"), TrainingStates.waiting_for_mode
)
async def select_mode_handler(
    callback: CallbackQuery, callback_data: TrainingCB, state: FSMContext
) -> None:
    data = await state.get_data()
    difficulty = Difficulty(data["difficulty"])
    mode = TrainingMode(callback_data.mode)
    lang = data.get("lang", "ru")

    cfg = DIFFICULTY_CONFIG[difficulty]
    examples_count = int(cfg["examples_count"])

    problems = ProblemGenerator.generate_problems(difficulty, mode, examples_count)
    session = await create_training_session(
        telegram_id=callback.from_user.id,
        difficulty=difficulty.value,
        mode=mode.value,
        total_problems=len(problems),
    )

    await state.update_data(
        session_id=session.id,
        difficulty=difficulty.value,
        mode=mode.value,
        problems=problems,
        idx=0,
        correct=0,
        incorrect=0,
        session_streak=0,
        last_time_s=None,
        anchor_chat_id=callback.message.chat.id,
        anchor_message_id=callback.message.message_id,
        current_problem_id=None,
        problem_shown_at=None,
        session_kind="normal",
        session_started_at=datetime.now(timezone.utc).isoformat(),
    )

    await show_problem(callback, state)
    await callback.answer()


# Backwards-compat entry: clicking "Start training" in the main menu used
# to fire MenuCB(action="training") which is also wired in inline.py.
from app.keyboards.callbacks import MenuCB  # noqa: E402 — late import to avoid cycle


@router.callback_query(MenuCB.filter(F.action == "training"))
async def start_training_handler(
    callback: CallbackQuery, callback_data: MenuCB, state: FSMContext
) -> None:
    lang = await get_user_language(callback.from_user.id)
    await state.clear()
    await state.update_data(lang=lang)
    await state.set_state(TrainingStates.waiting_for_difficulty)
    await safe_edit(
        callback,
        get_text("choose_difficulty", lang),
        InlineKeyboards.difficulty_selection(lang),
    )
    await callback.answer()


# Quick Start: skip both pickers, launch a session with the saved favorite.
# If favorite_difficulty is NULL we default to MEDIUM. If no favorite_mode is
# saved (race with Settings clearing it), fall back to the normal picker.
_QUICK_START_DEFAULT_DIFFICULTY = Difficulty.MEDIUM


@router.callback_query(MenuCB.filter(F.action == "quick_start"))
async def quick_start_handler(
    callback: CallbackQuery, callback_data: MenuCB, state: FSMContext
) -> None:
    lang = await get_user_language(callback.from_user.id)
    favorite_mode, favorite_difficulty = await get_user_favorite(callback.from_user.id)
    if not favorite_mode:
        await state.clear()
        await state.update_data(lang=lang)
        await state.set_state(TrainingStates.waiting_for_difficulty)
        await safe_edit(
            callback,
            get_text("choose_difficulty", lang),
            InlineKeyboards.difficulty_selection(lang),
        )
        await callback.answer()
        return

    try:
        mode = TrainingMode(favorite_mode)
    except ValueError:
        await callback.answer()
        return

    try:
        difficulty = (
            Difficulty(favorite_difficulty)
            if favorite_difficulty
            else _QUICK_START_DEFAULT_DIFFICULTY
        )
    except ValueError:
        difficulty = _QUICK_START_DEFAULT_DIFFICULTY
    cfg = DIFFICULTY_CONFIG[difficulty]
    examples_count = int(cfg["examples_count"])
    problems = ProblemGenerator.generate_problems(difficulty, mode, examples_count)

    session = await create_training_session(
        telegram_id=callback.from_user.id,
        difficulty=difficulty.value,
        mode=mode.value,
        total_problems=len(problems),
    )

    await state.clear()
    await state.update_data(
        lang=lang,
        session_id=session.id,
        difficulty=difficulty.value,
        mode=mode.value,
        problems=problems,
        idx=0,
        correct=0,
        incorrect=0,
        session_streak=0,
        last_time_s=None,
        anchor_chat_id=callback.message.chat.id,
        anchor_message_id=callback.message.message_id,
        current_problem_id=None,
        problem_shown_at=None,
        session_kind="normal",
        session_started_at=datetime.now(timezone.utc).isoformat(),
    )
    await show_problem(callback, state)
    await callback.answer()


# ---------------------------------------------------------------------------
# Unified renderers
# ---------------------------------------------------------------------------


async def show_problem(
    callback: CallbackQuery, state: FSMContext, feedback_prefix: str | None = None
) -> None:
    """Render the current problem into the anchor message.

    Works for both choose-answer (callback-driven) and type-answer (text-driven)
    modes — the keyboard branches on ``mode``, the rendering does not.
    """
    data = await state.get_data()
    problems: list[Problem] = data["problems"]
    idx = int(data["idx"])
    lang = data.get("lang", "ru")
    mode = TrainingMode(data["mode"])
    difficulty = Difficulty(data["difficulty"])
    session_id = int(data["session_id"])

    problem = problems[idx]

    # Persist the problem row so we can attach the answer + retry-mistakes later.
    problem_id = await record_problem_shown(
        session_id=session_id,
        first_number=problem.first_num,
        second_number=problem.second_num,
        operation=problem.operation,
        correct_answer=problem.answer,
        metadata=problem.metadata,
    )

    shown_at = datetime.now(timezone.utc)
    await state.update_data(
        current_problem_id=problem_id,
        problem_shown_at=shown_at.isoformat(),
    )

    text = format_problem_anchor(
        expression=problem.formatted_text,
        current=idx + 1,
        total=len(problems),
        lang=lang,
        streak=int(data.get("session_streak", 0)),
        last_time_s=data.get("last_time_s"),
        feedback_prefix=feedback_prefix,
    )

    if mode == TrainingMode.CHOOSE_ANSWER:
        keyboard = InlineKeyboards.training_type_controls(lang)
    else:
        cfg = DIFFICULTY_CONFIG[difficulty]
        variants = ProblemGenerator.generate_variants(problem.answer, int(cfg["variants_count"]))
        keyboard = InlineKeyboards.training_answer_variants(variants, idx, lang)

    await state.set_state(TrainingStates.waiting_for_answer)
    await safe_edit(callback, text, keyboard)


async def _edit_anchor_from_state(
    bot, state: FSMContext, text: str, reply_markup
) -> None:
    """Edit the tracked anchor message by stored chat_id + message_id."""
    data = await state.get_data()
    await edit_anchor(
        bot,
        chat_id=int(data["anchor_chat_id"]),
        message_id=int(data["anchor_message_id"]),
        text=text,
        reply_markup=reply_markup,
    )


async def _compute_last_time_s(state: FSMContext) -> float | None:
    data = await state.get_data()
    shown_iso = data.get("problem_shown_at")
    if not shown_iso:
        return None
    try:
        shown_at = datetime.fromisoformat(shown_iso)
    except ValueError:
        return None
    delta = (datetime.now(timezone.utc) - shown_at).total_seconds()
    return max(0.0, delta)


# ---------------------------------------------------------------------------
# Answer handlers
# ---------------------------------------------------------------------------


@router.callback_query(
    TrainingCB.filter(F.action == "answer"), TrainingStates.waiting_for_answer
)
async def handle_answer(
    callback: CallbackQuery, callback_data: TrainingCB, state: FSMContext
) -> None:
    user_answer = callback_data.answer
    await _record_and_advance(callback, state, user_answer=user_answer, skipped=False)
    await callback.answer()


@router.message(TrainingStates.waiting_for_answer, F.text)
async def handle_typed_answer(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get("mode") != TrainingMode.CHOOSE_ANSWER.value:
        return  # Other modes use the inline buttons exclusively.

    lang = data.get("lang", "ru")
    raw = (message.text or "").strip()

    # Always best-effort drop the user message so the chat stays clean.
    await delete_user_message(message)

    try:
        user_answer = int(raw)
    except (ValueError, AttributeError):
        # Re-render the anchor with an inline warning under the expression.
        problems: list[Problem] = data["problems"]
        idx = int(data["idx"])
        text = format_problem_anchor(
            expression=problems[idx].formatted_text,
            current=idx + 1,
            total=len(problems),
            lang=lang,
            streak=int(data.get("session_streak", 0)),
            last_time_s=data.get("last_time_s"),
            feedback_prefix=get_text("training_type_answer_invalid", lang),
        )
        await _edit_anchor_from_state(
            message.bot, state, text, InlineKeyboards.training_type_controls(lang)
        )
        return

    await _record_and_advance(message, state, user_answer=user_answer, skipped=False)


@router.callback_query(
    TrainingCB.filter(F.action == "skip"), TrainingStates.waiting_for_answer
)
async def handle_skip(
    callback: CallbackQuery, callback_data: TrainingCB, state: FSMContext
) -> None:
    await _record_and_advance(callback, state, user_answer=None, skipped=True)
    await callback.answer()


@router.callback_query(TrainingCB.filter(F.action == "exit"))
async def abort_training_handler(
    callback: CallbackQuery, callback_data: TrainingCB, state: FSMContext
) -> None:
    lang = await get_user_language(callback.from_user.id)
    await safe_edit(
        callback,
        get_text("training_abort", lang),
        InlineKeyboards.back_only(lang),
    )
    await state.clear()
    await callback.answer()


# ---------------------------------------------------------------------------
# Shared advance / finish logic
# ---------------------------------------------------------------------------


async def _record_and_advance(
    target: CallbackQuery | Message,
    state: FSMContext,
    *,
    user_answer: int | None,
    skipped: bool,
) -> None:
    """Persist the answer, update FSM counters, render next problem or finish."""
    data = await state.get_data()
    correct_answer = int(data["problems"][int(data["idx"])].answer)
    is_correct = (not skipped) and user_answer == correct_answer

    problem_id = data.get("current_problem_id")
    if problem_id:
        await record_problem_answered(int(problem_id), user_answer=user_answer, is_correct=is_correct)

    last_time_s = await _compute_last_time_s(state)
    correct = int(data["correct"]) + (1 if is_correct else 0)
    incorrect = int(data["incorrect"]) + (0 if is_correct else 1)
    session_streak = int(data.get("session_streak", 0))
    session_streak = session_streak + 1 if is_correct else 0

    next_idx = int(data["idx"]) + 1
    problems: list[Problem] = data["problems"]
    has_next = next_idx < len(problems)
    lang = data.get("lang", "ru")

    await state.update_data(
        correct=correct,
        incorrect=incorrect,
        session_streak=session_streak,
        last_time_s=last_time_s,
        idx=next_idx if has_next else int(data["idx"]),
    )

    if is_correct:
        feedback_prefix = get_text("training_correct_short", lang)
    elif skipped:
        feedback_prefix = get_text("training_skipped_short", lang).format(answer=correct_answer)
    else:
        feedback_prefix = get_text("training_incorrect_short", lang).format(answer=correct_answer)

    if has_next:
        await _show_next_problem(target, state, feedback_prefix)
    else:
        await finish_training(target, state, feedback_prefix)


async def _show_next_problem(
    target: CallbackQuery | Message, state: FSMContext, feedback_prefix: str
) -> None:
    """Render the next problem into the anchor regardless of caller shape."""
    if isinstance(target, CallbackQuery):
        await show_problem(target, state, feedback_prefix=feedback_prefix)
        return

    # Message path (typed answer): build text+kb, then edit the stored anchor.
    data = await state.get_data()
    problems: list[Problem] = data["problems"]
    idx = int(data["idx"])
    lang = data.get("lang", "ru")
    difficulty = Difficulty(data["difficulty"])
    mode = TrainingMode(data["mode"])
    session_id = int(data["session_id"])

    problem = problems[idx]
    problem_id = await record_problem_shown(
        session_id=session_id,
        first_number=problem.first_num,
        second_number=problem.second_num,
        operation=problem.operation,
        correct_answer=problem.answer,
        metadata=problem.metadata,
    )
    shown_at = datetime.now(timezone.utc)
    await state.update_data(
        current_problem_id=problem_id,
        problem_shown_at=shown_at.isoformat(),
    )

    text = format_problem_anchor(
        expression=problem.formatted_text,
        current=idx + 1,
        total=len(problems),
        lang=lang,
        streak=int(data.get("session_streak", 0)),
        last_time_s=data.get("last_time_s"),
        feedback_prefix=feedback_prefix,
    )

    if mode == TrainingMode.CHOOSE_ANSWER:
        keyboard = InlineKeyboards.training_type_controls(lang)
    else:
        cfg = DIFFICULTY_CONFIG[difficulty]
        variants = ProblemGenerator.generate_variants(problem.answer, int(cfg["variants_count"]))
        keyboard = InlineKeyboards.training_answer_variants(variants, idx, lang)

    await state.set_state(TrainingStates.waiting_for_answer)
    await _edit_anchor_from_state(target.bot, state, text, keyboard)


async def finish_training(
    target: CallbackQuery | Message,
    state: FSMContext,
    feedback_prefix: str | None = None,
) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    session_id = int(data["session_id"])
    correct = int(data["correct"])
    incorrect = int(data["incorrect"])
    total = correct + incorrect
    session_kind = data.get("session_kind", "normal")

    await complete_training_session(
        session_id=session_id,
        correct=correct,
        incorrect=incorrect,
    )

    if session_kind == "daily":
        daily_attempt_id = data.get("daily_attempt_id")
        session_started_iso = data.get("session_started_at")
        total_time_ms = 0
        if session_started_iso:
            try:
                started = datetime.fromisoformat(session_started_iso)
                total_time_ms = int(
                    (datetime.now(timezone.utc) - started).total_seconds() * 1000
                )
            except ValueError:
                pass
        if daily_attempt_id:
            await complete_daily_attempt(
                attempt_id=int(daily_attempt_id),
                correct=correct,
                incorrect=incorrect,
                total_time_ms=total_time_ms,
            )

    avg_time = await _session_avg_time(session_id)
    streak_delta = correct  # placeholder — full per-day delta would need user join
    body = format_session_result(
        correct=correct,
        total=total,
        avg_time_s=avg_time,
        streak_delta=streak_delta,
        lang=lang,
    )
    if feedback_prefix:
        body = feedback_prefix + "\n\n" + body

    has_mistakes = incorrect > 0 and session_kind != "daily"
    keyboard = InlineKeyboards.session_result(
        has_mistakes=has_mistakes, lang=lang, session_kind=session_kind
    )

    if isinstance(target, CallbackQuery):
        await safe_edit(target, body, keyboard)
    else:
        await _edit_anchor_from_state(target.bot, state, body, keyboard)

    # Preserve session_id / session_kind for retry; clear the rest.
    await state.set_state(TrainingStates.viewing_results)
    await state.update_data(
        problems=None,
        idx=0,
        correct=0,
        incorrect=0,
        session_streak=0,
        current_problem_id=None,
        problem_shown_at=None,
    )


async def _session_avg_time(session_id: int) -> float | None:
    """Average seconds per answered problem within this session."""
    from app.database.db import async_session_maker
    from app.database.models import Problem
    from sqlalchemy import func, select

    async with async_session_maker() as session:
        delta = func.extract("epoch", Problem.answered_at - Problem.shown_at)
        stmt = (
            select(func.avg(delta))
            .where(
                Problem.session_id == session_id,
                Problem.shown_at.is_not(None),
                Problem.answered_at.is_not(None),
            )
        )
        result = await session.execute(stmt)
        value = result.scalar()
        return float(value) if value is not None else None


# ---------------------------------------------------------------------------
# Retry mistakes
# ---------------------------------------------------------------------------


@router.callback_query(
    TrainingCB.filter(F.action == "retry_mistakes"), TrainingStates.viewing_results
)
async def retry_mistakes_handler(
    callback: CallbackQuery, callback_data: TrainingCB, state: FSMContext
) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    original_session_id = int(data["session_id"])
    original_mode = data.get("mode", TrainingMode.MIXED.value)
    original_difficulty = data.get("difficulty", Difficulty.EASY.value)

    mistake_rows = await get_session_mistakes(original_session_id)
    if not mistake_rows:
        await callback.answer(get_text("training_no_mistakes", lang), show_alert=True)
        return

    rebuilt: list[Problem] = []
    for row in mistake_rows:
        metadata = json.loads(row.metadata_json) if row.metadata_json else {}
        rebuilt.append(
            Problem(
                first_num=row.first_number,
                second_num=row.second_number,
                operation=row.operation,
                answer=row.correct_answer,
                formatted_text=metadata.get("formatted_text"),
                metadata=metadata,
            )
        )

    new_session = await create_training_session(
        telegram_id=callback.from_user.id,
        difficulty=original_difficulty,
        mode=original_mode,
        total_problems=len(rebuilt),
    )

    await state.set_state(TrainingStates.waiting_for_answer)
    await state.update_data(
        session_id=new_session.id,
        problems=rebuilt,
        idx=0,
        correct=0,
        incorrect=0,
        session_streak=0,
        last_time_s=None,
        current_problem_id=None,
        problem_shown_at=None,
        session_kind="retry",
    )
    await show_problem(callback, state)
    await callback.answer()
