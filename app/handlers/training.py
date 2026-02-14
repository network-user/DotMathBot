from __future__ import annotations

import logging

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.database.db import complete_training_session, create_training_session, get_user_language
from app.keyboards.inline import InlineKeyboards
from app.locales import get_text
from app.services.problem_generator import ProblemGenerator
from app.utils.constants import DIFFICULTY_CONFIG, Difficulty, TrainingMode

router = Router()
logger = logging.getLogger(__name__)


class TrainingStates(StatesGroup):
    waiting_for_difficulty = State()
    waiting_for_mode = State()
    waiting_for_answer = State()
    waiting_next = State()


async def safe_edit_text(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    try:
        await callback.message.edit_text(
            text, reply_markup=reply_markup, parse_mode="Markdown"
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return
        raise


def kb_after_answer(has_next: bool, lang: str = "ru") -> InlineKeyboardMarkup:
    row: list[InlineKeyboardButton] = []
    if has_next:
        row.append(
            InlineKeyboardButton(
                text=get_text("btn_next", lang),
                callback_data="next_problem",
            )
        )
    row.append(
        InlineKeyboardButton(
            text=get_text("btn_abort_training", lang),
            callback_data="abort_training",
        )
    )
    row2 = [
        InlineKeyboardButton(
            text=get_text("btn_back_to_menu", lang),
            callback_data="back_to_menu",
        )
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row, row2])


@router.callback_query(F.data == "start_training")
async def start_training_handler(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await get_user_language(callback.from_user.id)
    await state.update_data(lang=lang)
    logger.info("User %s started training", callback.from_user.id)
    text = get_text("choose_difficulty", lang)
    await state.set_state(TrainingStates.waiting_for_difficulty)
    await safe_edit_text(callback, text, InlineKeyboards.difficulty_selection(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("difficulty_"), TrainingStates.waiting_for_difficulty)
async def select_difficulty_handler(callback: CallbackQuery, state: FSMContext) -> None:
    difficulty_str = callback.data.split("_", 1)[1]
    await state.update_data(difficulty=difficulty_str)
    data = await state.get_data()
    lang = data.get("lang", "ru")

    text = get_text("choose_mode", lang)
    await state.set_state(TrainingStates.waiting_for_mode)
    await safe_edit_text(callback, text, InlineKeyboards.mode_selection(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("mode_"), TrainingStates.waiting_for_mode)
async def select_mode_handler(callback: CallbackQuery, state: FSMContext) -> None:
    mode_str = callback.data.split("_", 1)[1]
    data = await state.get_data()
    difficulty = Difficulty(data["difficulty"])
    mode = TrainingMode(mode_str)
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
        current_problem_answer=None,
    )

    await show_problem(callback, state)
    await callback.answer()


async def show_problem(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    problems = data["problems"]
    idx = int(data["idx"])
    lang = data.get("lang", "ru")

    difficulty = Difficulty(data["difficulty"])
    cfg = DIFFICULTY_CONFIG[difficulty]
    variants_count = int(cfg["variants_count"])

    problem = problems[idx]
    variants = ProblemGenerator.generate_variants(problem.answer, variants_count)

    await state.update_data(current_problem_answer=problem.answer)

    problem_text = f"{problem.first_num} {problem.operation} {problem.second_num}"
    text = get_text("training_problem", lang).format(
        current=idx + 1,
        total=len(problems),
        expr=problem_text,
    )

    await state.set_state(TrainingStates.waiting_for_answer)
    await safe_edit_text(
        callback,
        text,
        InlineKeyboards.training_answer_variants(variants, idx, lang),
    )


@router.callback_query(F.data.startswith("answer_"), TrainingStates.waiting_for_answer)
async def handle_answer(callback: CallbackQuery, state: FSMContext) -> None:
    _, idx_str, ans_str = callback.data.split("_")
    user_answer = int(ans_str)

    data = await state.get_data()
    correct_answer = int(data["current_problem_answer"])
    lang = data.get("lang", "ru")

    is_correct = user_answer == correct_answer

    correct = int(data["correct"]) + (1 if is_correct else 0)
    incorrect = int(data["incorrect"]) + (0 if is_correct else 1)

    next_idx = int(data["idx"]) + 1
    problems = data["problems"]
    has_next = next_idx < len(problems)

    await state.update_data(
        correct=correct,
        incorrect=incorrect,
        idx=next_idx,
    )

    if is_correct:
        feedback = get_text("training_correct", lang)
    else:
        feedback = get_text("training_incorrect", lang).format(answer=correct_answer)

    if has_next:
        await state.set_state(TrainingStates.waiting_next)
        next_prompt = get_text("training_next_prompt", lang)
        await safe_edit_text(
            callback,
            feedback + next_prompt,
            kb_after_answer(True, lang),
        )
    else:
        await finish_training(callback, state, feedback)

    await callback.answer()


@router.callback_query(F.data == "next_problem", TrainingStates.waiting_next)
async def next_problem_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await show_problem(callback, state)
    await callback.answer()


async def finish_training(
    callback: CallbackQuery, state: FSMContext, prefix: str = ""
) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")

    session_id = int(data["session_id"])
    correct = int(data["correct"])
    incorrect = int(data["incorrect"])
    total = correct + incorrect
    accuracy = (correct / total * 100.0) if total else 0.0

    await complete_training_session(
        session_id=session_id,
        correct=correct,
        incorrect=incorrect,
    )

    text = (
        (prefix + "\n\n" if prefix else "")
        + get_text("training_result_title", lang)
        + get_text("training_result_correct", lang).format(
            correct=correct, total=total
        )
        + get_text("training_result_incorrect", lang).format(
            incorrect=incorrect, total=total
        )
        + get_text("training_result_accuracy", lang).format(acc=accuracy)
        + get_text("training_well_done", lang)
    )

    await safe_edit_text(callback, text, InlineKeyboards.back_to_menu(lang))
    await state.clear()


@router.callback_query(F.data == "abort_training")
async def abort_training_handler(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await get_user_language(callback.from_user.id)
    text = get_text("training_abort", lang)
    await safe_edit_text(callback, text, InlineKeyboards.back_to_menu(lang))
    await state.clear()
    await callback.answer()
