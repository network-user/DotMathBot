"""Daily Challenge: a single shared 10-problem set per calendar day (Europe/Moscow).

All users see the same problem sequence — generated deterministically from a
SHA-256 hash of the date so adjacent days don't share PRNG structure.
Each user gets exactly one attempt per day; results are ranked by
(correct DESC, total_time_ms ASC) on the daily leaderboard.

The actual problem-rendering and answer-handling flow is reused from
``training.py`` via FSM ``session_kind = "daily"``.
"""
from __future__ import annotations

import hashlib
import logging
import random
from datetime import date, datetime, timezone
from typing import Optional

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.database.db import (
    create_training_session,
    get_or_create_daily_attempt,
    get_or_create_daily_challenge,
    get_or_create_user,
    get_user_language,
    has_user_done_daily,
)
from app.handlers.training import TrainingStates, show_problem
from app.keyboards.callbacks import MenuCB
from app.keyboards.inline import InlineKeyboards
from app.locales import get_text
from app.services.problem_generator import Problem, ProblemGenerator
from app.utils.constants import Difficulty, TrainingMode
from app.utils.ui import safe_edit, today_msk

router = Router()
logger = logging.getLogger(__name__)

DAILY_PROBLEM_COUNT = 10
_DAILY_OPERATIONS = (
    TrainingMode.ADDITION_ONLY,
    TrainingMode.SUBTRACTION_ONLY,
    TrainingMode.MULTIPLICATION_ONLY,
    TrainingMode.DIVISION_ONLY,
    TrainingMode.DIVISION_REMAINDER,
    TrainingMode.POWER_ONLY,
    TrainingMode.SQRT_ONLY,
)


def daily_seed(challenge_date: date) -> int:
    """Stable 32-bit seed for a given date.

    SHA-256 over a fixed namespace ("dotmath:YYYY-MM-DD") gives a uniform
    distribution that's resistant to adjacent-day PRNG correlation, which the
    Mersenne Twister exhibits for small adjacent seeds.
    """
    digest = hashlib.sha256(f"dotmath:{challenge_date.isoformat()}".encode()).hexdigest()
    return int(digest[:8], 16)


def generate_daily_specs(seed: int) -> list[dict]:
    """Deterministically generate 10 hard mixed-operation problem specs."""
    rng = random.Random(seed)
    specs: list[dict] = []
    for _ in range(DAILY_PROBLEM_COUNT):
        mode = rng.choice(_DAILY_OPERATIONS)
        problem = ProblemGenerator._generate_one(Difficulty.HARD, mode, rng=rng)
        specs.append(
            {
                "first_num": problem.first_num,
                "second_num": problem.second_num,
                "operation": problem.operation,
                "answer": problem.answer,
                "formatted_text": problem.formatted_text,
                "metadata": problem.metadata,
            }
        )
    return specs


def _specs_to_problems(specs: list[dict]) -> list[Problem]:
    return [
        Problem(
            first_num=int(s["first_num"]),
            second_num=int(s["second_num"]),
            operation=s["operation"],
            answer=int(s["answer"]),
            formatted_text=s.get("formatted_text"),
            metadata=s.get("metadata") or {},
        )
        for s in specs
    ]


@router.callback_query(MenuCB.filter(F.action == "daily"))
async def daily_entry_handler(
    callback: CallbackQuery, callback_data: MenuCB, state: FSMContext
) -> None:
    lang = await get_user_language(callback.from_user.id)
    user, _ = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
    )
    today = today_msk()

    if await has_user_done_daily(callback.from_user.id, today):
        await safe_edit(
            callback,
            get_text("daily_challenge_already_done", lang),
            InlineKeyboards.daily_already_done(lang),
        )
        await callback.answer()
        return

    challenge = await get_or_create_daily_challenge(today, generate_daily_specs, daily_seed)
    attempt, _created = await get_or_create_daily_attempt(user.id, today)
    problems = _specs_to_problems(list(challenge.problem_specs))

    # Synthetic training session row so we can persist Problem rows + retry would still work.
    new_session = await create_training_session(
        telegram_id=callback.from_user.id,
        difficulty=Difficulty.HARD.value,
        mode=TrainingMode.MIXED.value,
        total_problems=len(problems),
    )

    await state.clear()
    await state.update_data(
        lang=lang,
        session_id=new_session.id,
        difficulty=Difficulty.HARD.value,
        mode=TrainingMode.MIXED.value,
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
        session_kind="daily",
        daily_attempt_id=attempt.id,
        session_started_at=datetime.now(timezone.utc).isoformat(),
    )
    await state.set_state(TrainingStates.waiting_for_answer)
    await show_problem(callback, state)
    await callback.answer()
