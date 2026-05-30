import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.database.db import (
    get_or_create_user,
    get_user_favorite,
    get_user_language,
    has_user_done_daily,
    update_user_language,
)
from app.handlers.training import TrainingStates
from app.keyboards.callbacks import BackCB, MenuCB
from app.keyboards.inline import InlineKeyboards
from app.locales import get_text
from app.utils.ui import today_msk

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
        logger.info(
            "New user registered: id=%s username=%s",
            message.from_user.id,
            message.from_user.username,
        )

    await state.clear()

    lang = getattr(user, "language", None) or "ru"
    daily_done = await has_user_done_daily(message.from_user.id, today_msk())
    favorite_mode = getattr(user, "favorite_mode", None)
    favorite_difficulty = getattr(user, "favorite_difficulty", None)
    name = message.from_user.first_name or get_text("welcome_fallback_name", lang)
    text = get_text("welcome", lang).format(name=name)

    await message.answer(text, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    await message.answer(
        get_text("main_menu", lang),
        reply_markup=InlineKeyboards.main_menu(
            lang,
            daily_done=daily_done,
            favorite_mode=favorite_mode,
            favorite_difficulty=favorite_difficulty,
        ),
        parse_mode="Markdown",
    )


@router.callback_query(MenuCB.filter(F.action.in_({"lang_ru", "lang_en"})))
async def language_switch_handler(
    callback: CallbackQuery, callback_data: MenuCB, state: FSMContext
) -> None:
    lang = "en" if callback_data.action == "lang_en" else "ru"
    await update_user_language(callback.from_user.id, lang)
    msg_key = "language_changed_en" if lang == "en" else "language_changed"
    await callback.answer(get_text(msg_key, lang))
    daily_done = await has_user_done_daily(callback.from_user.id, today_msk())
    favorite_mode, favorite_difficulty = await get_user_favorite(callback.from_user.id)
    await callback.message.edit_text(
        get_text("main_menu", lang),
        reply_markup=InlineKeyboards.main_menu(
            lang,
            daily_done=daily_done,
            favorite_mode=favorite_mode,
            favorite_difficulty=favorite_difficulty,
        ),
        parse_mode="Markdown",
    )


@router.message(Command("train"))
async def train_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await get_user_language(message.from_user.id)
    await state.set_state(TrainingStates.waiting_for_difficulty)
    await state.update_data(lang=lang)
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
        reply_markup=InlineKeyboards.back_only(lang),
        parse_mode="Markdown",
    )


@router.message(Command("top"))
async def top_command(message: Message) -> None:
    from app.services.stats_service import StatsService

    lang = await get_user_language(message.from_user.id)
    text = await StatsService.get_leaderboard_choose_mode_text(lang)
    await message.answer(
        text,
        reply_markup=InlineKeyboards.leaderboard_mode_choice(lang),
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
    """Open the Settings hub (favorite mode, notifications, privacy, language)."""
    from app.database.db import get_user

    lang = await get_user_language(message.from_user.id)
    user = await get_user(message.from_user.id)
    favorite_mode = getattr(user, "favorite_mode", None) if user else None
    show_in_top = bool(getattr(user, "show_in_top", False)) if user else False

    await message.answer(
        get_text("settings_title", lang),
        reply_markup=InlineKeyboards.settings_menu(
            lang, favorite_mode=favorite_mode, show_in_top=show_in_top
        ),
        parse_mode="Markdown",
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    text = get_text("help", lang)
    await message.answer(text, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    await message.answer(
        get_text("main_menu", lang),
        reply_markup=InlineKeyboards.back_only(lang),
        parse_mode="Markdown",
    )


@router.callback_query(BackCB.filter(F.action == "menu"))
async def back_to_menu_handler(
    callback: CallbackQuery, callback_data: BackCB, state: FSMContext
) -> None:
    await state.clear()
    lang = await get_user_language(callback.from_user.id)
    daily_done = await has_user_done_daily(callback.from_user.id, today_msk())
    favorite_mode, favorite_difficulty = await get_user_favorite(callback.from_user.id)
    await callback.message.edit_text(
        get_text("main_menu", lang),
        reply_markup=InlineKeyboards.main_menu(
            lang,
            daily_done=daily_done,
            favorite_mode=favorite_mode,
            favorite_difficulty=favorite_difficulty,
        ),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(MenuCB.filter(F.action == "help"))
async def menu_help_handler(callback: CallbackQuery, callback_data: MenuCB) -> None:
    lang = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        get_text("help", lang),
        reply_markup=InlineKeyboards.back_only(lang),
        parse_mode="Markdown",
    )
    await callback.answer()
