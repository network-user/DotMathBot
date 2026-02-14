import logging
from functools import partial

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards.inline import InlineKeyboards
from app.database.db import update_user_notifications, get_user_language, get_user
from app.locales import get_text
from app.utils.constants import NotificationPreset, NOTIFICATION_PRESETS
from app.services.notification_callback import send_training_reminder

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "settings_notifications")
async def settings_notifications_handler(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    text = get_text("settings_notifications", lang)
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.notification_preset_selection(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("notify_preset_"))
async def notify_preset_handler(callback: CallbackQuery, state: FSMContext) -> None:
    from app.main import get_notification_service

    preset_str = callback.data.split("_")[-1]
    preset = NotificationPreset(preset_str)
    lang = await get_user_language(callback.from_user.id)

    logger.info(f"User {callback.from_user.id} selected notification preset: {preset_str}")

    if preset == NotificationPreset.CUSTOM:
        text = get_text("custom_time_unavailable", lang)
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboards.back_to_menu(lang),
            parse_mode="Markdown"
        )
        await callback.answer(get_text("feature_unavailable", lang), show_alert=True)
        return

    await update_user_notifications(callback.from_user.id, preset_str)

    try:
        service = get_notification_service()
        bot = callback.bot

        if preset == NotificationPreset.DISABLED:
            service.unschedule_user(callback.from_user.id)
            text = get_text("notifications_disabled", lang)
            logger.info(f"Notifications disabled for user {callback.from_user.id}")
        else:
            config = NOTIFICATION_PRESETS[preset]

            if not config["times"]:
                text = get_text("preset_config_error", lang).format(name=config["name"])
                logger.error(f"Preset {preset_str} has no times configured")
            else:
                callback_func = partial(send_training_reminder, bot)
                service.schedule_user(
                    telegram_id=callback.from_user.id,
                    times=config["times"],
                    callback=callback_func,
                )

                times_str = ", ".join([t.strftime("%H:%M") for t in config["times"]])
                preset_keys = {
                    NotificationPreset.MORNING: "notify_preset_morning",
                    NotificationPreset.LUNCH: "notify_preset_lunch",
                    NotificationPreset.EVENING: "notify_preset_evening",
                    NotificationPreset.THREE_TIMES: "notify_preset_three",
                }
                preset_name = get_text(preset_keys.get(preset, "notify_preset_morning"), lang)
                text = get_text("notifications_set", lang).format(
                    name=preset_name,
                    times=times_str,
                )
                logger.info(f"Scheduled {len(config['times'])} reminders for user {callback.from_user.id}")

    except Exception as e:
        logger.error(f"Failed to update notification schedule for user {callback.from_user.id}: {e}", exc_info=True)
        text = get_text("notification_error", lang)

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.back_to_menu(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "check_notifications")
async def check_notifications_handler(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    user = await get_user(callback.from_user.id)

    if not user or not user.notification_enabled:
        text = get_text("notifications_disabled", lang)
    else:
        preset_str = user.notification_preset or "disabled"
        try:
            preset = NotificationPreset(preset_str)
            config = NOTIFICATION_PRESETS.get(preset)

            if config and config["times"]:
                times_str = ", ".join([t.strftime("%H:%M") for t in config["times"]])
                preset_keys = {
                    NotificationPreset.MORNING: "notify_preset_morning",
                    NotificationPreset.LUNCH: "notify_preset_lunch",
                    NotificationPreset.EVENING: "notify_preset_evening",
                    NotificationPreset.THREE_TIMES: "notify_preset_three",
                }
                preset_name = get_text(preset_keys.get(preset, "notify_preset_morning"), lang)
                text = get_text("current_notifications", lang).format(
                    name=preset_name,
                    times=times_str,
                )
            else:
                text = get_text("preset_misconfigured", lang).format(preset=preset_str)
        except ValueError:
            text = get_text("unknown_preset", lang).format(preset=preset_str)

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.back_to_menu(lang),
        parse_mode="Markdown"
    )
    await callback.answer()
