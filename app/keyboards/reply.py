"""Reply keyboards (кнопки под полем ввода)."""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.locales import get_text


def abort_training(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой «Прервать тренировку» (только для режима «Напиши ответ сам»)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text("btn_abort_training_full", lang))],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
