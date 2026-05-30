"""Settings hub: 2-step favorite picker + entry point for prefs.

The hub itself lives at ``MenuCB(action="settings")``. Sub-actions
(language, notifications, privacy toggle) are re-routed to their existing
handlers — this module owns only the favorite flow + the hub render.

Favorite picker is two steps to keep Quick Start unambiguous: step 1 picks
``difficulty``, step 2 picks ``mode`` (with difficulty carried in callback
data so expand/collapse don't lose it).
"""
from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.database.db import (
    get_user,
    get_user_favorite,
    get_user_language,
    update_user_favorite,
    update_user_show_in_top,
)
from app.keyboards.callbacks import MenuCB, ProfileCB, SettingsCB
from app.keyboards.inline import InlineKeyboards, difficulty_label
from app.locales import get_text
from app.utils.ui import safe_edit

router = Router()
logger = logging.getLogger(__name__)


async def _render_settings(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    user = await get_user(callback.from_user.id)
    show_in_top = user.show_in_top if user else False
    favorite_mode = user.favorite_mode if user else None
    favorite_difficulty = user.favorite_difficulty if user else None
    await safe_edit(
        callback,
        get_text("settings_title", lang),
        InlineKeyboards.settings_menu(
            lang,
            favorite_mode=favorite_mode,
            favorite_difficulty=favorite_difficulty,
            show_in_top=show_in_top,
        ),
    )


@router.callback_query(MenuCB.filter(F.action == "settings"))
async def open_settings_from_menu_handler(
    callback: CallbackQuery, callback_data: MenuCB
) -> None:
    await _render_settings(callback)
    await callback.answer()


@router.callback_query(SettingsCB.filter(F.action == "open"))
async def open_settings_handler(
    callback: CallbackQuery, callback_data: SettingsCB
) -> None:
    await _render_settings(callback)
    await callback.answer()


@router.callback_query(SettingsCB.filter(F.action == "favorite_open"))
async def favorite_pick_difficulty_handler(
    callback: CallbackQuery, callback_data: SettingsCB
) -> None:
    """Step 1: difficulty picker."""
    lang = await get_user_language(callback.from_user.id)
    _, current_difficulty = await get_user_favorite(callback.from_user.id)
    await safe_edit(
        callback,
        get_text("favorite_choose_difficulty_title", lang),
        InlineKeyboards.favorite_difficulty_selection(
            lang, current_difficulty=current_difficulty
        ),
    )
    await callback.answer()


@router.callback_query(
    SettingsCB.filter(
        F.action.in_({"favorite_difficulty", "favorite_more", "favorite_less"})
    )
)
async def favorite_pick_mode_handler(
    callback: CallbackQuery, callback_data: SettingsCB
) -> None:
    """Step 2: mode picker, with difficulty carried in callback data."""
    lang = await get_user_language(callback.from_user.id)
    current_mode, _ = await get_user_favorite(callback.from_user.id)
    expanded = callback_data.action == "favorite_more"
    diff_str = callback_data.difficulty or "medium"
    title = get_text("favorite_choose_mode_title", lang).format(
        difficulty=difficulty_label(diff_str, lang)
    )
    await safe_edit(
        callback,
        title,
        InlineKeyboards.favorite_mode_selection(
            lang,
            current_mode=current_mode,
            expanded=expanded,
            difficulty=diff_str,
        ),
    )
    await callback.answer()


@router.callback_query(SettingsCB.filter(F.action == "favorite_set"))
async def favorite_set_handler(
    callback: CallbackQuery, callback_data: SettingsCB
) -> None:
    lang = await get_user_language(callback.from_user.id)
    await update_user_favorite(
        callback.from_user.id,
        mode=callback_data.mode,
        difficulty=callback_data.difficulty or "medium",
    )
    await _render_settings(callback)
    await callback.answer(get_text("favorite_saved", lang))


@router.callback_query(SettingsCB.filter(F.action == "favorite_clear"))
async def favorite_clear_handler(
    callback: CallbackQuery, callback_data: SettingsCB
) -> None:
    lang = await get_user_language(callback.from_user.id)
    await update_user_favorite(callback.from_user.id, mode=None, difficulty=None)
    await _render_settings(callback)
    await callback.answer(get_text("favorite_cleared", lang))


# Privacy toggle. ``ProfileCB(action="toggle_top")`` is now only triggered
# from the Settings hub — the redundant copy on the profile screen was removed.
@router.callback_query(ProfileCB.filter(F.action == "toggle_top"))
async def toggle_top_privacy_handler(
    callback: CallbackQuery, callback_data: ProfileCB
) -> None:
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer()
        return
    await update_user_show_in_top(callback.from_user.id, not user.show_in_top)
    await _render_settings(callback)
    await callback.answer()
