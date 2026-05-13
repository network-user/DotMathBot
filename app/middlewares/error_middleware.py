"""Catches unhandled exceptions from handlers and sends a friendly reply."""
from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.database.db import get_user_language
from app.locales import get_text

logger = logging.getLogger(__name__)


class ErrorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception:
            logger.exception("Unhandled error in handler")
            await self._notify_user(event)
            return None

    async def _notify_user(self, event: TelegramObject) -> None:
        try:
            user_id = getattr(getattr(event, "from_user", None), "id", None)
            lang = await get_user_language(user_id) if user_id else "ru"
            text = get_text("internal_error", lang)
        except Exception:
            text = "⚠️ Произошла внутренняя ошибка. Попробуйте позже."

        try:
            if isinstance(event, CallbackQuery):
                await event.answer(text, show_alert=True)
            elif isinstance(event, Message):
                await event.answer(text)
        except Exception:
            logger.debug("Could not deliver error notice to user", exc_info=True)
