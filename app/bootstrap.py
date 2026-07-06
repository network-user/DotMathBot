"""Bot setup and run: initializes DB, bot, dispatcher, services, handlers."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import NamedTuple
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import ADMIN_IDS, BOT_TOKEN, DB_PATH, REDIS_URL
from app.database.db import init_db
from app.handlers import admin, daily, notifications, profile, settings, start, training
from app.locales import get_text
from app.middlewares.error_middleware import ErrorMiddleware
from app.services.backup_service import BackupService, _scrub_secrets
from app.services.notification_loader import load_scheduled_users
from app.services.notification_service import NotificationService
from app.utils.set_commands import set_bot_commands

logger = logging.getLogger(__name__)

HEARTBEAT_FILE = Path(DB_PATH) / ".heartbeat"
HEARTBEAT_INTERVAL_SECONDS = 30


async def _heartbeat_loop() -> None:
    """Refresh a heartbeat file so the container HEALTHCHECK can tell the polling
    loop is alive: a wedged event loop stops updating the file's mtime."""
    try:
        HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        logger.warning("Heartbeat dir create failed: %s", exc)
    while True:
        try:
            HEARTBEAT_FILE.write_text("ok")
        except OSError as exc:
            logger.warning("Heartbeat write failed: %s", exc)
        await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)


async def notify_admins_startup(bot: Bot, reminders_count: int) -> None:
    """Best-effort ping every admin that the bot just came up.

    Sends are wrapped in try/except — a blocked or unknown admin shouldn't
    abort the startup flow. ADMIN_IDS that haven't ever started the bot will
    fail with TelegramForbiddenError; we log and move on.
    """
    if not ADMIN_IDS:
        return

    timestamp = datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M MSK")
    text = get_text("admin_startup_notification", "ru").format(
        timestamp=timestamp,
        reminders_count=reminders_count,
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, parse_mode="Markdown")
        except (TelegramBadRequest, TelegramForbiddenError) as e:
            logger.warning("Startup notification to admin %s failed: %s", admin_id, e)


class App(NamedTuple):
    bot: Bot
    dp: Dispatcher
    notification_service: NotificationService
    backup_service: BackupService


def _build_fsm_storage() -> BaseStorage:
    """Return RedisStorage when REDIS_URL is configured, else MemoryStorage.

    Memory storage loses every active training session on restart — fine for
    local dev. Production runs in compose should always point REDIS_URL at the
    redis service so mid-training users survive a redeploy.
    """
    if not REDIS_URL:
        logger.info("REDIS_URL not set — using in-memory FSM storage")
        return MemoryStorage()

    from aiogram.fsm.storage.redis import RedisStorage
    storage = RedisStorage.from_url(REDIS_URL)
    # Scrub any password in the DSN before logging (redis://user:pass@host).
    logger.info("Using Redis FSM storage at %s", _scrub_secrets(REDIS_URL))
    return storage


async def setup_app() -> App:
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")

    bot = Bot(token=BOT_TOKEN)
    storage = _build_fsm_storage()
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
    dp.include_router(settings.router)
    dp.include_router(admin.router)
    logger.info("Handlers registered successfully")

    logger.info(
        "Bot setup complete. Active reminders: %s",
        notification_service.get_all_jobs_count(),
    )

    return App(bot=bot, dp=dp, notification_service=notification_service, backup_service=backup_service)


async def run_app(app: App) -> None:
    heartbeat_task = asyncio.create_task(_heartbeat_loop())
    try:
        await notify_admins_startup(
            app.bot, reminders_count=app.notification_service.get_all_jobs_count()
        )
        logger.info("Bot started and listening for updates...")
        await app.dp.start_polling(
            app.bot,
            allowed_updates=app.dp.resolve_used_update_types(),
        )
    finally:
        heartbeat_task.cancel()
        logger.info("Shutting down bot...")
        app.notification_service.shutdown()
        app.backup_service.scheduler.shutdown()
        await app.bot.session.close()
        logger.info("Bot stopped")
