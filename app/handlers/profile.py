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
    await callback.message.edit_text(
        profile_text,
        reply_markup=InlineKeyboards.back_to_menu(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "show_leaderboard")
async def show_leaderboard_handler(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    leaderboard_text = await StatsService.get_formatted_leaderboard(lang=lang)
    await callback.message.edit_text(
        leaderboard_text,
        reply_markup=InlineKeyboards.back_to_menu(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


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
