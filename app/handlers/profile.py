import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.db import get_user, get_user_language, update_user_show_in_top
from app.keyboards.callbacks import LeaderboardCB, MenuCB, ProfileCB, TipsCB
from app.keyboards.inline import InlineKeyboards
from app.locales import get_text
from app.services.hint_service import get_tips
from app.services.stats_service import StatsService

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(MenuCB.filter(F.action == "profile"))
async def show_profile_handler(callback: CallbackQuery, callback_data: MenuCB) -> None:
    lang = await get_user_language(callback.from_user.id)
    profile_text = await StatsService.get_formatted_profile(callback.from_user.id, lang)
    user = await get_user(callback.from_user.id)
    show_in_top = user.show_in_top if user else True

    await callback.message.edit_text(
        profile_text,
        reply_markup=InlineKeyboards.back_to_menu(lang, show_in_top),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(MenuCB.filter(F.action == "leaderboard"))
async def show_leaderboard_handler(callback: CallbackQuery, callback_data: MenuCB) -> None:
    lang = await get_user_language(callback.from_user.id)
    text = await StatsService.get_leaderboard_choose_mode_text(lang)
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.leaderboard_mode_choice(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(LeaderboardCB.filter(F.action == "page"))
async def show_leaderboard_mode_handler(
    callback: CallbackQuery, callback_data: LeaderboardCB
) -> None:
    lang = await get_user_language(callback.from_user.id)
    mode = callback_data.mode
    offset = callback_data.page

    leaderboard_text, has_next = await StatsService.get_formatted_leaderboard(
        limit=10,
        offset=offset,
        lang=lang,
        mode=mode,
        telegram_id=callback.from_user.id,
    )
    await callback.message.edit_text(
        leaderboard_text,
        reply_markup=InlineKeyboards.leaderboard_mode_choice(lang, mode, offset, has_next),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(ProfileCB.filter(F.action == "toggle_top"))
async def toggle_top_privacy_handler(
    callback: CallbackQuery, callback_data: ProfileCB
) -> None:
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


@router.callback_query(MenuCB.filter(F.action == "tips"))
async def show_tips_handler(callback: CallbackQuery, callback_data: MenuCB) -> None:
    lang = await get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        get_text("tips_choose", lang),
        reply_markup=InlineKeyboards.tips_menu(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


async def _render_tip(callback: CallbackQuery, category: str) -> None:
    lang = await get_user_language(callback.from_user.id)
    text = get_tips(category, lang)
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.tips_menu(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(TipsCB.filter(F.action == "multiplication"))
async def tips_multiplication_handler(
    callback: CallbackQuery, callback_data: TipsCB
) -> None:
    await _render_tip(callback, "multiplication")


@router.callback_query(TipsCB.filter(F.action == "division"))
async def tips_division_handler(callback: CallbackQuery, callback_data: TipsCB) -> None:
    await _render_tip(callback, "division")


@router.callback_query(TipsCB.filter(F.action == "general"))
async def tips_general_handler(callback: CallbackQuery, callback_data: TipsCB) -> None:
    await _render_tip(callback, "general")
