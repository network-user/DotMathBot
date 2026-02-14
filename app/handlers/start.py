import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.keyboards.inline import InlineKeyboards
from app.database.db import get_or_create_user, get_user_language, update_user_language
from app.locales import get_text

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    user, created = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    if created:
        logger.info("New user registered: id=%s username=%s", message.from_user.id, message.from_user.username)

    await state.clear()

    lang = getattr(user, "language", None) or "ru"
    name = message.from_user.first_name or get_text("welcome_fallback_name", lang)
    text = get_text("welcome", lang).format(name=name)

    await message.answer(
        text,
        reply_markup=InlineKeyboards.main_menu(lang),
        parse_mode="Markdown",
    )


@router.callback_query(F.data.in_({"lang_ru", "lang_en"}))
async def language_switch_handler(callback: CallbackQuery, state: FSMContext) -> None:
    lang = "en" if callback.data == "lang_en" else "ru"
    await update_user_language(callback.from_user.id, lang)
    msg_key = "language_changed_en" if lang == "en" else "language_changed"
    await callback.answer(get_text(msg_key, lang))
    text = get_text("main_menu", lang)
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.main_menu(lang),
        parse_mode="Markdown",
    )


@router.message(Command("train"))
async def train_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await get_user_language(message.from_user.id)
    text = get_text("choose_difficulty", lang)
    await message.answer(
        text,
        reply_markup=InlineKeyboards.difficulty_selection(lang),
        parse_mode="Markdown",
    )


@router.message(Command("profile"))
async def profile_command(message: Message) -> None:
    from app.services.stats_service import StatsService

    lang = await get_user_language(message.from_user.id)
    profile_text = await StatsService.get_formatted_profile(message.from_user.id, lang)
    await message.answer(
        profile_text,
        reply_markup=InlineKeyboards.back_to_menu(lang),
        parse_mode="Markdown",
    )


@router.message(Command("top"))
async def top_command(message: Message) -> None:
    from app.services.stats_service import StatsService

    lang = await get_user_language(message.from_user.id)
    leaderboard_text = await StatsService.get_formatted_leaderboard(lang=lang)
    await message.answer(
        leaderboard_text,
        reply_markup=InlineKeyboards.back_to_menu(lang),
        parse_mode="Markdown",
    )


@router.message(Command("tips"))
async def tips_command(message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    text = get_text("tips_choose", lang)
    await message.answer(
        text,
        reply_markup=InlineKeyboards.tips_menu(lang),
        parse_mode="Markdown",
    )


@router.message(Command("settings"))
async def settings_command(message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    text = get_text("settings_notifications", lang)
    await message.answer(
        text,
        reply_markup=InlineKeyboards.notification_preset_selection(lang),
        parse_mode="Markdown",
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    text = get_text("help", lang)
    await message.answer(
        text,
        reply_markup=InlineKeyboards.back_to_menu(lang),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = await get_user_language(callback.from_user.id)
    text = get_text("main_menu", lang)
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.main_menu(lang),
        parse_mode="Markdown",
    )
    await callback.answer()
