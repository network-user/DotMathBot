import asyncio
import logging
from functools import partial

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import BOT_TOKEN, DEBUG
from app.database.db import init_db, get_all_users_with_notifications
from app.handlers import start, training, profile, notifications
from app.utils.logger import setup_logging
from app.utils.set_commands import set_bot_commands
from app.services.notification_service import NotificationService
from app.services.notification_callback import send_training_reminder
from app.utils.constants import NotificationPreset, NOTIFICATION_PRESETS

setup_logging(
    logs_dir="logs",
    log_level=logging.DEBUG if DEBUG else logging.INFO,
)

logger = logging.getLogger(__name__)

notification_service: NotificationService | None = None
# ToDO: Весь лишний функционал позже вынести в отдельные модули

def get_notification_service() -> NotificationService:
    global notification_service
    if notification_service is None:
        raise RuntimeError("NotificationService not initialized")
    return notification_service


async def load_scheduled_users(bot: Bot, service: NotificationService) -> None:
    logger.info("Loading users with enabled notifications...")

    users = await get_all_users_with_notifications()

    if not users:
        logger.info("No users with active notifications found")
        return

    scheduled_count = 0

    for user in users:
        try:
            preset = NotificationPreset(user.notification_preset)

            if preset == NotificationPreset.CUSTOM:
                custom_times = NotificationService.parse_times(user.custom_notification_times)
                if not custom_times:
                    logger.warning(f"User {user.telegram_id} has custom preset but no times configured")
                    continue
                times = custom_times
            else:
                config = NOTIFICATION_PRESETS.get(preset)
                if not config or not config["times"]:
                    logger.warning(f"No times configured for preset {preset.value} (user {user.telegram_id})")
                    continue
                times = config["times"]

            callback = partial(send_training_reminder, bot)

            service.schedule_user(
                telegram_id=int(user.telegram_id),
                times=times,
                callback=callback,
            )
            scheduled_count += 1

        except Exception as e:
            logger.error(f"Failed to load notifications for user {user.telegram_id}: {e}")

    logger.info(f"Loaded reminders for {scheduled_count} users")


async def main() -> None:
    global notification_service

    try:
        logger.info("Starting bot...")

        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")

        bot = Bot(token=BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        logger.info("Initializing NotificationService...")
        notification_service = NotificationService(timezone="Europe/Moscow")
        notification_service.start()

        await load_scheduled_users(bot, notification_service)
        await set_bot_commands(bot)

        logger.info("Registering handlers...")
        dp.include_router(start.router)
        dp.include_router(training.router)
        dp.include_router(profile.router)
        dp.include_router(notifications.router)
        logger.info("Handlers registered successfully")

        logger.info("Bot started and listening for updates...")
        logger.info(f"Active reminders: {notification_service.get_all_jobs_count()}")

        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as e:
        logger.critical(f"Critical error during bot startup: {e}", exc_info=True)
        raise

    finally:
        logger.info("Shutting down bot...")
        if notification_service:
            notification_service.shutdown()
        if 'bot' in locals():
            await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())