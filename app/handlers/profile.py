import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.keyboards.inline import InlineKeyboards
from app.database.db import get_user_language
from app.services.stats_service import StatsService
from app.services.hint_service import get_tips

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "show_profile")
async def show_profile_handler(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    profile_text = await StatsService.get_formatted_profile(callback.from_user.id, lang)
    from app.database.db import get_user
    user = await get_user(callback.from_user.id)
    show_in_top = user.show_in_top if user else True
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=InlineKeyboards.back_to_menu(lang, show_in_top),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "show_leaderboard")
async def show_leaderboard_handler(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    text = await StatsService.get_leaderboard_choose_mode_text(lang)
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.leaderboard_mode_choice(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.regexp(r"leaderboard_(streak|solved|accuracy|weighted):(\d+)"))
async def show_leaderboard_mode_handler(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    data = callback.data.split(":")
    mode = data[0].replace("leaderboard_", "")
    offset = int(data[1])
    
    leaderboard_text, has_next = await StatsService.get_formatted_leaderboard(
        limit=10, offset=offset, lang=lang, mode=mode, telegram_id=callback.from_user.id
    )
    await callback.message.edit_text(
        leaderboard_text,
        reply_markup=InlineKeyboards.leaderboard_mode_choice(lang, mode, offset, has_next),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_top_privacy")
async def toggle_top_privacy_handler(callback: CallbackQuery) -> None:
    from app.database.db import get_user, update_user_show_in_top
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден.")
        return
        
    new_value = not user.show_in_top
    await update_user_show_in_top(callback.from_user.id, new_value)
    
    lang = await get_user_language(callback.from_user.id)
    profile_text = await StatsService.get_formatted_profile(callback.from_user.id, lang)
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=InlineKeyboards.back_to_menu(lang, new_value),
        parse_mode="Markdown",
    )
    await callback.answer("Настройки обновлены!")


@router.callback_query(F.data == "show_tips")
async def show_tips_handler(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    from app.locales import get_text

    text = get_text("tips_choose", lang)
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.tips_menu(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "tips_multiplication")
async def tips_multiplication_handler(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    text = get_tips("multiplication", lang)
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.tips_menu(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "tips_division")
async def tips_division_handler(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    text = get_tips("division", lang)
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.tips_menu(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "tips_general")
async def tips_general_handler(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    text = get_tips("general", lang)
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.tips_menu(lang),
        parse_mode="Markdown",
    )
    await callback.answer()
