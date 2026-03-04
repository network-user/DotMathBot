import os
import shutil
import logging
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from app.config import DB_PATH, ADMIN_IDS

logger = logging.getLogger(__name__)

class BackupService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.backups_dir = os.path.join(DB_PATH, "backups")
        os.makedirs(self.backups_dir, exist_ok=True)

    async def create_backup(self):
        """Создает резервную копию базы данных."""
        db_file = os.path.join(DB_PATH, "bot.db")
        if not os.path.exists(db_file):
            logger.error("DB file not found at %s", db_file)
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"bot_backup_{timestamp}.db"
        backup_path = os.path.join(self.backups_dir, backup_name)

        try:
            shutil.copy2(db_file, backup_path)
            logger.info("Backup created: %s", backup_name)
            
            await self._cleanup_old_backups()
            await self._notify_admins(backup_name)
            return backup_path
        except Exception as e:
            logger.error("Error creating backup: %s", e)
            return None

    async def _cleanup_old_backups(self):
        """Удаляет старые бэкапы, оставляя только 20 последних."""
        backups = sorted(
            [f for f in os.listdir(self.backups_dir) if f.startswith("bot_backup_")],
            key=lambda x: os.path.getmtime(os.path.join(self.backups_dir, x))
        )
        
        while len(backups) > 20:
            oldest_backup = backups.pop(0)
            os.remove(os.path.join(self.backups_dir, oldest_backup))
            logger.info("Old backup removed: %s", oldest_backup)

    async def _notify_admins(self, backup_name: str):
        """Уведомляет администраторов об успешном создании бэкапа."""
        message = f"✅ **Резервная копия БД создана успешно!**\n\n📄 Файл: `{backup_name}`\n⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        for admin_id in ADMIN_IDS:
            try:
                await self.bot.send_message(admin_id, message, parse_mode="Markdown")
            except Exception as e:
                logger.warning("Failed to notify admin %s: %s", admin_id, e)

    def start(self):
        """Запускает планировщик бэкапов (каждые 12 часов)."""
        self.scheduler.add_job(self.create_backup, 'interval', hours=12)
        self.scheduler.start()
        logger.info("Backup scheduler started (every 12 hours)")
