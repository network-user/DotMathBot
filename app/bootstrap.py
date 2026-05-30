"""Bot setup and run: initializes DB, bot, dispatcher, services, handlers."""
from __future__ import annotations

import logging
from typing import NamedTuple

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import BOT_TOKEN
from app.database.db import init_db
from app.handlers import admin, daily, notifications, profile, start, training
from app.middlewares.error_middleware import ErrorMiddleware
from app.services.backup_service import BackupService
from app.services.notification_loader import load_scheduled_users
from app.services.notification_service import NotificationService
from app.utils.set_commands import set_bot_commands

logger = logging.getLogger(__name__)


class App(NamedTuple):
    bot: Bot
    dp: Dispatcher
    notification_service: NotificationService
    backup_service: BackupService


async def setup_app() -> App:
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    logger.info("Initializing NotificationService...")
    notification_service = NotificationService(timezone="Europe/Moscow")
    notification_service.start()

    # DI: services flow to handlers via dispatcher workflow data.
    dp["notification_service"] = notification_service

    await load_scheduled_users(bot, notification_service)
    await set_bot_commands(bot)

    logger.info("Initializing BackupService...")
    backup_service = BackupService(bot)
    backup_service.start()

    dp.update.middleware(ErrorMiddleware())

    logger.info("Registering handlers...")
    dp.include_router(start.router)
    dp.include_router(daily.router)
    dp.include_router(training.router)
    dp.include_router(profile.router)
    dp.include_router(notifications.router)
    dp.include_router(admin.router)
    logger.info("Handlers registered successfully")

    logger.info(
        "Bot setup complete. Active reminders: %s",
        notification_service.get_all_jobs_count(),
    )

    return App(bot=bot, dp=dp, notification_service=notification_service, backup_service=backup_service)


async def run_app(app: App) -> None:
    try:
        logger.info("Bot started and listening for updates...")
        await app.dp.start_polling(
            app.bot,
            allowed_updates=app.dp.resolve_used_update_types(),
        )
    finally:
        logger.info("Shutting down bot...")
        app.notification_service.shutdown()
        app.backup_service.scheduler.shutdown()
        await app.bot.session.close()
        logger.info("Bot stopped")
