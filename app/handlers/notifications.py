import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards.inline import InlineKeyboards
from app.database.db import update_user_notifications, get_user_language
from app.locales import get_text
from app.utils.constants import NotificationPreset, NOTIFICATION_PRESETS

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
    preset_str = callback.data.split("_")[-1]
    preset = NotificationPreset(preset_str)
    lang = await get_user_language(callback.from_user.id)

    await update_user_notifications(callback.from_user.id, preset_str)
    logger.info("User %s set notification preset to %s", callback.from_user.id, preset_str)

    config = NOTIFICATION_PRESETS[preset]

    if preset == NotificationPreset.DISABLED:
        text = get_text("notifications_disabled", lang)
    else:
        times_str = ", ".join([t.strftime("%H:%M") for t in config["times"]])
        preset_keys = {
            NotificationPreset.MORNING: "notify_preset_morning",
            NotificationPreset.LUNCH: "notify_preset_lunch",
            NotificationPreset.EVENING: "notify_preset_evening",
            NotificationPreset.THREE_TIMES: "notify_preset_three",
            NotificationPreset.CUSTOM: "notify_preset_custom",
        }
        preset_name = get_text(preset_keys.get(preset, "notify_preset_three"), lang)
        text = get_text("notifications_set", lang).format(
            name=preset_name,
            times=times_str,
        )

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.back_to_menu(lang),
        parse_mode="Markdown",
    )
    await callback.answer(text[:100])
