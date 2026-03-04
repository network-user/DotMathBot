import logging
import psutil
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile

from app.config import ADMIN_IDS, DB_PATH, ADMIN_BACKUP_PASSWORD
from app.keyboards.inline import InlineKeyboards
from app.database.db import get_total_users_count, get_new_users_count, get_all_users_paginated

class AdminStates(StatesGroup):
    wait_backup_password = State()

router = Router()
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_panel_handler(message: Message) -> None:
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "🛠 **Панель администратора**\n\nВыберите действие:",
        reply_markup=InlineKeyboards.admin_main_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin_main")
async def admin_main_callback(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав!", show_alert=True)
        return

    await callback.message.edit_text(
        "🛠 **Панель администратора**\n\nВыберите действие:",
        reply_markup=InlineKeyboards.admin_main_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin_stats")
async def admin_stats_handler(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        return

    # Нагрузка сервера
    cpu_usage = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    
    # Статистика пользователей
    total_users = await get_total_users_count()
    new_today = await get_new_users_count(1)
    new_week = await get_new_users_count(7)

    stats_text = (
        "📊 **Статистика бота**\n\n"
        f"🖥 **Сервер:**\n"
        f"• CPU: `{cpu_usage}%`\n"
        f"• RAM: `{ram.percent}%` ({round(ram.used / (1024**3), 2)} GB / {round(ram.total / (1024**3), 2)} GB)\n\n"
        f"👥 **Пользователи:**\n"
        f"• Всего: `{total_users}`\n"
        f"• Новых за сегодня: `{new_today}`\n"
        f"• Новых за неделю: `{new_week}`"
    ).replace("**3", "^3") # Избегаем конфликта с Markdown bold

    await callback.message.edit_text(
        stats_text,
        reply_markup=InlineKeyboards.admin_main_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.regexp(r"admin_users:(\d+)"))
async def admin_users_list_handler(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        return

    offset = int(callback.data.split(":")[1])
    limit = 10
    users = await get_all_users_paginated(limit, offset)
    
    if not users and offset == 0:
        await callback.message.edit_text("Пользователей пока нет.", reply_markup=InlineKeyboards.admin_main_menu())
        return

    text = f"👥 **Список пользователей (смещение {offset}):**\n\n"
    for user in users:
        raw_first_name = user.first_name or ""
        raw_username = user.username or "нет username"
        
        # Экранируем Markdown спецсимволы
        safe_first_name = raw_first_name.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
        safe_username = raw_username.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
        
        prefix = f"@{safe_username}" if user.username else safe_username
        text += f"• ID: `{user.telegram_id}` | {safe_first_name} ({prefix})\n"
    
    has_next = len(users) == limit
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboards.admin_users_list(offset, has_next),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin_backup")
async def admin_backup_handler(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        return

    from app.services.backup_service import BackupService
    backup_service = BackupService(callback.bot)
    await backup_service.create_backup()
    await callback.answer("Бэкап успешно создан!", show_alert=True)

@router.callback_query(F.data == "admin_download_backup")
async def admin_download_backup_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        return

    await state.set_state(AdminStates.wait_backup_password)
    await callback.message.answer("⌨️ Введите пароль для выгрузки бэкапа:")
    await callback.answer()

@router.message(AdminStates.wait_backup_password)
async def admin_download_backup_process(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    password = message.text
    # Сразу удаляем сообщение с паролем для безопасности
    try:
        await message.delete()
    except Exception:
        pass

    if password == ADMIN_BACKUP_PASSWORD:
        from app.services.backup_service import BackupService
        backup_service = BackupService(message.bot)
        
        await message.answer("🔄 Создаю свежий бэкап и подготавливаю файл...")
        try:
            backup_path = await backup_service.create_backup()
            
            if backup_path:
                # Конвертируем в строку для документов и Path методов
                path_str = str(backup_path)
                filename = os.path.basename(path_str)
                
                document = FSInputFile(path_str)
                await message.bot.send_document(
                    message.chat.id, 
                    document, 
                    caption=f"💾 Резервная копия от {filename}"
                )
            else:
                await message.answer("❌ Ошибка при создании файла бэкапа. Проверьте логи сервера.")
        except Exception as e:
            await message.answer(f"❌ Критическая ошибка при бэкапе: `{str(e)}`", parse_mode="Markdown")
    else:
        await message.answer("❌ Неверный пароль. Доступ отклонен.")
    
    await state.clear()
