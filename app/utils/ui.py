"""Shared UI rendering helpers for the anchor-message training paradigm.

The whole bot edits a single "anchor" message per session instead of sending
new ones; these helpers keep that paradigm consistent across handlers.

- ``render_progress_bar`` / ``format_seconds`` — pure rendering primitives.
- ``format_problem_anchor`` — the standard data-dense problem screen.
- ``format_session_result`` — the compact end-of-session block.
- ``safe_edit`` — swallows aiogram's "message is not modified" race noise.
- ``delete_user_message`` — best-effort cleanup for type-answer mode where
  the user's reply would otherwise pile up in the chat.
- ``today_msk`` — calendar boundary for daily challenges (Europe/Moscow,
  matching the notification scheduler in ``notification_service``).
"""
from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Optional
from zoneinfo import ZoneInfo

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from app.locales import get_text

logger = logging.getLogger(__name__)

# Visible Unicode block chars chosen for monospace alignment in Telegram clients.
_BAR_FILLED = "▓"
_BAR_EMPTY = "░"
SEPARATOR = "────────────────"
_MSK = ZoneInfo("Europe/Moscow")


def render_progress_bar(current: int, total: int, width: int = 10) -> str:
    """Return a fixed-width ``▓▓▓░░░`` bar.

    ``current`` is 1-indexed (display semantics: "problem 3 of 10" means
    3 of 10 cells filled). Returns empty string when ``total`` is non-positive.
    """
    if total <= 0:
        return ""
    if current < 0:
        current = 0
    if current > total:
        current = total
    filled = round(current / total * width)
    filled = max(0, min(width, filled))
    return _BAR_FILLED * filled + _BAR_EMPTY * (width - filled)


def format_seconds(seconds: Optional[float]) -> str:
    """Render seconds as ``"4.2s"`` / ``"12s"``. None → empty string."""
    if seconds is None or seconds < 0:
        return ""
    if seconds < 10:
        return f"{seconds:.1f}s"
    return f"{int(round(seconds))}s"


def format_problem_anchor(
    expression: str,
    current: int,
    total: int,
    lang: str,
    streak: int = 0,
    last_time_s: Optional[float] = None,
    feedback_prefix: Optional[str] = None,
) -> str:
    """Build the standard problem screen body.

    Layout (top-to-bottom, blank lines for breathing room):

        {feedback from previous turn}

        🧮 Пример N / M
        ▓▓▓░░░░░░░░░

           **expression = ?**

        🔥 серия 3   ⏱ 4.2s
    """
    bar = render_progress_bar(current, total)
    header = get_text("training_anchor_header", lang).format(
        current=current, total=total, bar=bar
    )

    footer_parts: list[str] = []
    if streak > 0:
        footer_parts.append(f"🔥 серия {streak}" if lang == "ru" else f"🔥 streak {streak}")
    if last_time_s is not None:
        footer_parts.append(f"⏱ {format_seconds(last_time_s)}")
    footer = "   ".join(footer_parts)

    blocks: list[str] = []
    if feedback_prefix:
        blocks.append(feedback_prefix)
    blocks.append(header)
    blocks.append(f"   **{expression} = ?**")
    if footer:
        blocks.append(footer)
    return "\n\n".join(blocks)


def format_session_result(
    correct: int,
    total: int,
    avg_time_s: Optional[float],
    streak_delta: int,
    lang: str,
) -> str:
    """Compact end-of-session block."""
    accuracy = (correct / total * 100) if total else 0.0
    return get_text("training_result_v2", lang).format(
        correct=correct,
        total=total,
        acc=round(accuracy),
        avg_time=format_seconds(avg_time_s) if avg_time_s else "—",
        streak_delta=streak_delta,
    )


async def safe_edit(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str = "Markdown",
) -> None:
    """Edit the anchor via callback.message; swallow "message is not modified"."""
    try:
        await callback.message.edit_text(
            text, reply_markup=reply_markup, parse_mode=parse_mode
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return
        raise


async def edit_anchor(
    bot,
    chat_id: int,
    message_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str = "Markdown",
) -> None:
    """Edit a specific message by (chat_id, message_id) — used by type-answer mode."""
    try:
        await bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return
        raise


async def delete_user_message(message: Message) -> None:
    """Best-effort cleanup: drop the user's reply so the chat stays clean.

    Telegram allows bots to delete user messages in private chats. In groups
    we may lack the permission; either way we swallow the error.
    """
    try:
        await message.delete()
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        logger.debug("delete_user_message suppressed: %s", e)


def today_msk() -> date:
    """Today in Europe/Moscow — the calendar boundary for daily challenges."""
    return datetime.now(_MSK).date()
