import hmac
import logging
import os

import psutil
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message

from app.config import ADMIN_BACKUP_PASSWORD, ADMIN_IDS
from app.database.db import (
    get_all_users_paginated,
    get_new_users_count,
    get_total_users_count,
    get_user_language,
)
from app.keyboards.callbacks import AdminCB
from app.keyboards.inline import InlineKeyboards
from app.locales import get_text


class AdminStates(StatesGroup):
    wait_backup_password = State()


router = Router()
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def _escape_md(value: str) -> str:
    return value.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")


@router.message(Command("admin"))
async def admin_panel_handler(message: Message) -> None:
    if not is_admin(message.from_user.id):
        return

    lang = await get_user_language(message.from_user.id)
    await message.answer(
        get_text("admin_panel_title", lang),
        reply_markup=InlineKeyboards.admin_main_menu(lang),
        parse_mode="Markdown",
    )


@router.callback_query(AdminCB.filter(F.action == "main"))
async def admin_main_callback(callback: CallbackQuery, callback_data: AdminCB) -> None:
    lang = await get_user_language(callback.from_user.id)
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("admin_no_rights", lang), show_alert=True)
        return

    await callback.message.edit_text(
        get_text("admin_panel_title", lang),
        reply_markup=InlineKeyboards.admin_main_menu(lang),
        parse_mode="Markdown",
    )


@router.callback_query(AdminCB.filter(F.action == "stats"))
async def admin_stats_handler(callback: CallbackQuery, callback_data: AdminCB) -> None:
    if not is_admin(callback.from_user.id):
        return

    lang = await get_user_language(callback.from_user.id)
    cpu_usage = psutil.cpu_percent()
    ram = psutil.virtual_memory()

    total_users = await get_total_users_count()
    new_today = await get_new_users_count(1)
    new_week = await get_new_users_count(7)

    stats_text = get_text("admin_stats_template", lang).format(
        cpu=cpu_usage,
        ram_pct=ram.percent,
        ram_used=round(ram.used / (1024 ** 3), 2),
        ram_total=round(ram.total / (1024 ** 3), 2),
        total=total_users,
        new_today=new_today,
        new_week=new_week,
    )

    await callback.message.edit_text(
        stats_text,
        reply_markup=InlineKeyboards.admin_main_menu(lang),
        parse_mode="Markdown",
    )


@router.callback_query(AdminCB.filter(F.action == "users"))
async def admin_users_list_handler(callback: CallbackQuery, callback_data: AdminCB) -> None:
    if not is_admin(callback.from_user.id):
        return

    lang = await get_user_language(callback.from_user.id)
    offset = callback_data.page
    limit = 10
    users = await get_all_users_paginated(limit, offset)

    if not users and offset == 0:
        await callback.message.edit_text(
            get_text("admin_users_empty", lang),
            reply_markup=InlineKeyboards.admin_main_menu(lang),
        )
        return

    page = offset // limit + 1
    text = get_text("admin_users_header", lang).format(page=page)
    no_username_label = get_text("admin_users_no_username", lang)
    for user in users:
        raw_first_name = user.first_name or ""
        raw_username = user.username or no_username_label

        safe_first_name = _escape_md(raw_first_name)
        safe_username = _escape_md(raw_username)

        prefix = f"@{safe_username}" if user.username else safe_username
        text += f"• ID: `{user.telegram_id}` | {safe_first_name} ({prefix})\n"

    has_next = len(users) == limit
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.admin_users_list(offset, has_next, lang),
        parse_mode="Markdown",
    )


@router.callback_query(AdminCB.filter(F.action == "backup"))
async def admin_backup_handler(callback: CallbackQuery, callback_data: AdminCB) -> None:
    if not is_admin(callback.from_user.id):
        return

    lang = await get_user_language(callback.from_user.id)
    from app.services.backup_service import BackupService

    backup_service = BackupService(callback.bot)
    await backup_service.create_backup()
    await callback.answer(get_text("admin_backup_ok", lang), show_alert=True)


@router.callback_query(AdminCB.filter(F.action == "download"))
async def admin_download_backup_prompt(
    callback: CallbackQuery, callback_data: AdminCB, state: FSMContext
) -> None:
    if not is_admin(callback.from_user.id):
        return

    lang = await get_user_language(callback.from_user.id)
    await state.set_state(AdminStates.wait_backup_password)
    await callback.message.answer(get_text("admin_backup_prompt", lang))
    await callback.answer()


@router.message(AdminStates.wait_backup_password)
async def admin_download_backup_process(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    lang = await get_user_language(message.from_user.id)
    password = message.text or ""
    try:
        await message.delete()
    except Exception:
        pass

    if hmac.compare_digest(password.encode("utf-8"), ADMIN_BACKUP_PASSWORD.encode("utf-8")):
        from app.services.backup_service import BackupService

        backup_service = BackupService(message.bot)
        await message.answer(get_text("admin_backup_creating", lang))
        try:
            backup_path = await backup_service.create_backup()

            if backup_path:
                path_str = str(backup_path)
                filename = os.path.basename(path_str)
                document = FSInputFile(path_str)
                await message.bot.send_document(
                    message.chat.id,
                    document,
                    caption=get_text("admin_backup_caption", lang).format(filename=filename),
                )
            else:
                await message.answer(get_text("admin_backup_file_error", lang))
        except Exception as e:
            await message.answer(
                get_text("admin_backup_critical_error", lang).format(error=str(e)),
                parse_mode="Markdown",
            )
    else:
        await message.answer(get_text("admin_backup_wrong_password", lang))

    await state.clear()
