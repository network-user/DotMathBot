"""
Bot setup and run: initializes DB, bot, dispatcher, notification service, and handlers.
Keeps main.py minimal.
"""
from __future__ import annotations

import logging
from typing import NamedTuple

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import BOT_TOKEN, DEBUG
from app.database.db import init_db
from app.handlers import start, training, profile, notifications
from app.utils.set_commands import set_bot_commands
from app.services.notification_service import NotificationService
from app.services.notification_loader import load_scheduled_users
from app.context import set_notification_service

logger = logging.getLogger(__name__)


class App(NamedTuple):
    """Holds bot, dispatcher and notification service after setup."""

    bot: Bot
    dp: Dispatcher
    notification_service: NotificationService


async def setup_app() -> App:
    """
    Initialize database, create bot and dispatcher, start notification service,
    load scheduled users, set commands, register handlers.
    """
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    logger.info("Initializing NotificationService...")
    notification_service = NotificationService(timezone="Europe/Moscow")
    notification_service.start()
    set_notification_service(notification_service)

    await load_scheduled_users(bot, notification_service)
    await set_bot_commands(bot)

    logger.info("Registering handlers...")
    dp.include_router(start.router)
    dp.include_router(training.router)
    dp.include_router(profile.router)
    dp.include_router(notifications.router)
    logger.info("Handlers registered successfully")

    logger.info(
        "Bot setup complete. Active reminders: %s",
        notification_service.get_all_jobs_count(),
    )

    return App(bot=bot, dp=dp, notification_service=notification_service)


async def run_app(app: App) -> None:
    """Start polling and run until stopped. Cleans up on exit."""
    try:
        logger.info("Bot started and listening for updates...")
        await app.dp.start_polling(
            app.bot,
            allowed_updates=app.dp.resolve_used_update_types(),
        )
    finally:
        logger.info("Shutting down bot...")
        app.notification_service.shutdown()
        await app.bot.session.close()
        logger.info("Bot stopped")
