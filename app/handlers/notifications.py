import logging
from datetime import time
from functools import partial

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards.inline import InlineKeyboards
from app.database.db import update_user_notifications, get_user_language, get_user
from app.locales import get_text
from app.utils.constants import NotificationPreset, NOTIFICATION_PRESETS
from app.services.notification_callback import send_training_reminder

router = Router()
logger = logging.getLogger(__name__)

class NotificationStates(StatesGroup):
    waiting_for_custom_time = State()


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
    preset_str = callback.data.split("_")[-1]
    preset = NotificationPreset(preset_str)
    lang = await get_user_language(callback.from_user.id)

    logger.info(f"User {callback.from_user.id} selected notification preset: {preset_str}")

    if preset == NotificationPreset.CUSTOM:
        await state.set_state(NotificationStates.waiting_for_custom_time)
        text = get_text("custom_time_input", lang)
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboards.cancel_custom_time(lang),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    await update_user_notifications(callback.from_user.id, preset_str)

    try:
        from app.context import get_notification_service

        try:
            service = get_notification_service()
        except RuntimeError:
            logger.warning(f"NotificationService not available, only DB updated for user {callback.from_user.id}")
            service = None

        if service:
            bot = callback.bot

            if preset == NotificationPreset.DISABLED:
                service.unschedule_user(callback.from_user.id)
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
                    logger.info(f"Scheduled {len(config['times'])} reminders for user {callback.from_user.id}")

        if preset == NotificationPreset.DISABLED:
            text = get_text("notifications_disabled", lang)
        else:
            config = NOTIFICATION_PRESETS[preset]
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

    except Exception as e:
        logger.error(f"Failed to update notification schedule for user {callback.from_user.id}: {e}", exc_info=True)
        text = get_text("notification_error", lang)

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.back_to_menu(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(NotificationStates.waiting_for_custom_time)
async def custom_time_input_handler(message: Message, state: FSMContext) -> None:
    from app.context import get_notification_service

    lang = await get_user_language(message.from_user.id)

    times_input = message.text.strip()
    parsed_times = parse_custom_times(times_input)

    if not parsed_times:
        text = get_text("custom_time_invalid", lang)
        await message.answer(
            text,
            reply_markup=InlineKeyboards.cancel_custom_time(lang),
            parse_mode="Markdown"
        )
        return

    await state.clear()

    custom_times_str = [t.strftime("%H:%M") for t in parsed_times]
    await update_user_notifications(
        message.from_user.id,
        "custom",
        custom_times=custom_times_str
    )

    try:
        service = get_notification_service()
        bot = message.bot

        callback_func = partial(send_training_reminder, bot)
        service.schedule_user(
            telegram_id=message.from_user.id,
            times=parsed_times,
            callback=callback_func,
        )

        times_str = ", ".join(custom_times_str)
        text = get_text("notifications_set", lang).format(
            name=get_text("notify_preset_custom", lang),
            times=times_str,
        )
        logger.info(f"Scheduled {len(parsed_times)} custom reminders for user {message.from_user.id}")

    except Exception as e:
        logger.error(f"Failed to schedule custom times for user {message.from_user.id}: {e}", exc_info=True)
        text = get_text("notification_error", lang)

    await message.answer(
        text,
        reply_markup=InlineKeyboards.back_to_menu(lang),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "cancel_custom_time")
async def cancel_custom_time_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = await get_user_language(callback.from_user.id)
    text = get_text("custom_time_cancelled", lang)
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.back_to_menu(lang),
        parse_mode="Markdown"
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

            if preset == NotificationPreset.CUSTOM:
                from app.services.notification_service import NotificationService
                custom_times = NotificationService.parse_times(user.custom_notification_times)

                if custom_times:
                    times_str = ", ".join([t.strftime("%H:%M") for t in custom_times])
                    text = get_text("current_notifications", lang).format(
                        name=get_text("notify_preset_custom", lang),
                        times=times_str,
                    )
                else:
                    text = get_text("preset_misconfigured", lang).format(preset=preset_str)
            else:
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


def parse_custom_times(text: str) -> list[time]:
    times = []
    parts = [p.strip() for p in text.replace(',', ' ').replace(';', ' ').split() if p.strip()]

    for part in parts:
        try:
            if ':' in part:
                h, m = part.split(':')
                hour, minute = int(h), int(m)
            elif len(part) == 4:
                hour, minute = int(part[:2]), int(part[2:])
            else:
                continue

            if 0 <= hour <= 23 and 0 <= minute <= 59:
                times.append(time(hour, minute))
        except (ValueError, IndexError):
            continue

    return times