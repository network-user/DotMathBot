"""Load scheduled notification reminders from DB into NotificationService on startup."""
from __future__ import annotations

import logging
from functools import partial

from aiogram import Bot

from app.database.db import get_all_users_with_notifications
from app.services.notification_service import NotificationService
from app.services.notification_callback import send_training_reminder
from app.utils.constants import NotificationPreset, NOTIFICATION_PRESETS

logger = logging.getLogger(__name__)


async def load_scheduled_users(bot: Bot, service: NotificationService) -> int:
    """
    Load all users with enabled notifications from DB and schedule their reminders.
    Returns the number of users for whom reminders were scheduled.
    """
    logger.info("Loading users with enabled notifications...")

    users = await get_all_users_with_notifications()

    if not users:
        logger.info("No users with active notifications found")
        return 0

    scheduled_count = 0

    for user in users:
        try:
            preset = NotificationPreset(user.notification_preset)

            if preset == NotificationPreset.CUSTOM:
                custom_times = NotificationService.parse_times(user.custom_notification_times)
                if not custom_times:
                    logger.warning(
                        "User %s has custom preset but no times configured",
                        user.telegram_id,
                    )
                    continue
                times = custom_times
            else:
                config = NOTIFICATION_PRESETS.get(preset)
                if not config or not config["times"]:
                    logger.warning(
                        "No times configured for preset %s (user %s)",
                        preset.value,
                        user.telegram_id,
                    )
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
            logger.error(
                "Failed to load notifications for user %s: %s",
                user.telegram_id,
                e,
                exc_info=True,
            )

    logger.info("Loaded reminders for %s users", scheduled_count)
    return scheduled_count
