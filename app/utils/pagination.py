"""Reusable pagination helpers."""
from __future__ import annotations

from typing import Any

from aiogram.types import InlineKeyboardButton

from app.utils.constants import PAGE_SIZE

__all__ = ["PAGE_SIZE", "build_pagination_row"]


def build_pagination_row(
    *,
    page: int,
    has_next: bool,
    callback_factory: Any,
    prev_text: str = "⬅️",
    next_text: str = "➡️",
    **factory_kwargs: Any,
) -> list[InlineKeyboardButton]:
    """Build a back/forward navigation row using a CallbackData factory.

    ``page`` is zero-based. The factory must accept ``page`` as a field.
    """
    row: list[InlineKeyboardButton] = []
    if page > 0:
        row.append(
            InlineKeyboardButton(
                text=prev_text,
                callback_data=callback_factory(page=page - 1, **factory_kwargs).pack(),
            )
        )
    if has_next:
        row.append(
            InlineKeyboardButton(
                text=next_text,
                callback_data=callback_factory(page=page + 1, **factory_kwargs).pack(),
            )
        )
    return row
