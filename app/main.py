import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import BOT_TOKEN, DEBUG
from app.database.db import init_db
from app.handlers import start, training, profile, notifications
from app.utils.logger import setup_logging
from app.utils.set_commands import set_bot_commands

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

setup_logging(
    logs_dir="logs",
    log_level=logging.DEBUG if DEBUG else logging.INFO,
)


logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Initializing the database...")
    await init_db()
    logger.info("The database has been successfully initialized")

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    await set_bot_commands(bot)

    logger.info("Registering handlers...")
    dp.include_router(start.router)
    dp.include_router(training.router)
    dp.include_router(profile.router)
    dp.include_router(notifications.router)

    logger.info("The handlers are registered")

    try:
        logger.info("The bot is running and starts listening for updates...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.critical(f"Critical error when launching the bot: {e}", exc_info=True)
        raise
    finally:
        logger.info("Shutting down the bot...")
        if 'bot' in locals():
            await bot.session.close()
        logger.info("The bot has been stopped")


if __name__ == "__main__":
    asyncio.run(main())