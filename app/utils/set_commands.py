import logging
from aiogram import Bot
from aiogram.types import BotCommand


logger = logging.getLogger(__name__)

# (slash_name, ru_description, en_description). Telegram picks the entry whose
# language_code matches the user's client language; default (no language_code)
# is shown for everyone else, so we use Russian for the default to match the
# default UI language of the bot.
_COMMANDS: tuple[tuple[str, str, str], ...] = (
    ("start",    "🏠 Главное меню",        "🏠 Main menu"),
    ("train",    "🎓 Начать тренировку",   "🎓 Start training"),
    ("profile",  "👤 Мой профиль",         "👤 My profile"),
    ("top",      "🏆 Топ пользователей",   "🏆 Leaderboard"),
    ("tips",     "💡 Шпаргалки",           "💡 Tips"),
    ("settings", "⚙️ Настройки",           "⚙️ Settings"),
    ("help",     "❓ Помощь",              "❓ Help"),
)


async def set_bot_commands(bot: Bot) -> None:
    """Register the slash-command menu in both RU and EN.

    Telegram serves the entry whose ``language_code`` matches the user's
    client locale; the call without ``language_code`` is the fallback for
    every other locale.
    """
    ru = [BotCommand(command=c, description=ru_text) for c, ru_text, _ in _COMMANDS]
    en = [BotCommand(command=c, description=en_text) for c, _, en_text in _COMMANDS]
    await bot.set_my_commands(ru)
    await bot.set_my_commands(en, language_code="en")
    logger.info("Bot commands installed (ru default + en)")