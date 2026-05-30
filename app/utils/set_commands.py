import logging
from aiogram import Bot
from aiogram.types import BotCommand


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def set_bot_commands(bot: Bot) -> None:
    """Set bot commands for the menu."""
    commands = [
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="train", description="🎓 Начать тренировку"),
        BotCommand(command="profile", description="📊 Мой профиль"),
        BotCommand(command="top", description="🏆 Топ пользователей"),
        BotCommand(command="tips", description="💡 Шпаргалки"),
        BotCommand(command="settings", description="⚙️ Настройки"),
        BotCommand(command="help", description="❓ Помощь"),
    ]
    await bot.set_my_commands(commands)
    logger.info("The bot commands are installed")