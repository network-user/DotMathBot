"""PostgreSQL backup service.

Spawns `pg_dump` via asyncio subprocess to produce a custom-format dump
(`.dump`) which can be restored with `pg_restore`. Runs every 12 hours,
retains the 20 most recent files, and notifies admins (with file size +
exit code) after each run.
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit, urlunsplit

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from app.config import ADMIN_IDS, DATABASE_URL, DB_PATH

logger = logging.getLogger(__name__)

BACKUP_RETENTION = 20
BACKUP_FILENAME_PREFIX = "bot_backup_"
BACKUP_FILENAME_SUFFIX = ".dump"


def _to_libpq_url(url: str) -> str:
    """Convert SQLAlchemy URL (postgresql+asyncpg://…) to libpq form for pg_dump."""
    for prefix in ("postgresql+asyncpg://", "postgresql+psycopg://", "postgresql+psycopg2://"):
        if url.startswith(prefix):
            return "postgresql://" + url[len(prefix):]
    return url


_DSN_CREDENTIALS_RE = re.compile(r"(?P<scheme>\w+://)(?P<user>[^:@/\s]+):[^@/\s]+@")


def _scrub_secrets(text: str) -> str:
    """Mask the password in any ``scheme://user:pass@host`` URL before the text
    is logged or sent to admins, so pg_dump stderr can't surface credentials."""
    return _DSN_CREDENTIALS_RE.sub(r"\g<scheme>\g<user>:***@", text)


def _split_libpq_url(url: str) -> tuple[str, str | None]:
    """Split a libpq URL into (dsn_without_password, password).

    The password is handed to pg_dump via ``PGPASSWORD`` instead of the DSN so
    it stays out of the process arg list (visible in ``ps``/``docker inspect``)."""
    libpq = _to_libpq_url(url)
    parsed = urlsplit(libpq)
    if parsed.password is None:
        return libpq, None
    userinfo, _, hostport = parsed.netloc.rpartition("@")
    user = userinfo.split(":", 1)[0]
    new_netloc = f"{user}@{hostport}" if user else hostport
    sanitized = urlunsplit(
        (parsed.scheme, new_netloc, parsed.path, parsed.query, parsed.fragment)
    )
    return sanitized, parsed.password


def _format_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


class BackupService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.backups_dir = Path(DB_PATH) / "backups"
        try:
            self.backups_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error("Could not create backups directory %s: %s", self.backups_dir, e)

    async def create_backup(self) -> Path | None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_name = f"{BACKUP_FILENAME_PREFIX}{timestamp}{BACKUP_FILENAME_SUFFIX}"
        backup_path = self.backups_dir / backup_name

        dsn, pg_password = _split_libpq_url(DATABASE_URL)
        env = os.environ.copy()
        if pg_password is not None:
            env["PGPASSWORD"] = pg_password
        proc = await asyncio.create_subprocess_exec(
            "pg_dump",
            "--format=custom",
            "--no-owner",
            "--no-acl",
            f"--dbname={dsn}",
            f"--file={backup_path}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        stdout, stderr = await proc.communicate()
        exit_code = proc.returncode or 0

        if exit_code != 0 or not backup_path.exists():
            err_text = _scrub_secrets(
                (stderr or b"").decode("utf-8", errors="replace").strip()
            )
            logger.error(
                "pg_dump failed (exit=%s): %s", exit_code, err_text or "<no stderr>"
            )
            await self._notify_admins_failure(backup_name, exit_code, err_text)
            return None

        size = backup_path.stat().st_size
        logger.info("Backup created: %s (%s)", backup_name, _format_size(size))
        await self._cleanup_old_backups()
        await self._notify_admins_success(backup_name, size, exit_code)
        return backup_path

    async def _cleanup_old_backups(self) -> None:
        backups = sorted(
            self._existing_backups(),
            key=lambda p: p.stat().st_mtime,
        )
        while len(backups) > BACKUP_RETENTION:
            oldest = backups.pop(0)
            try:
                oldest.unlink()
                logger.info("Old backup removed: %s", oldest.name)
            except OSError as e:
                logger.warning("Failed to delete old backup %s: %s", oldest, e)

    def _existing_backups(self) -> Iterable[Path]:
        return [
            p
            for p in self.backups_dir.glob(f"{BACKUP_FILENAME_PREFIX}*{BACKUP_FILENAME_SUFFIX}")
            if p.is_file()
        ]

    async def _notify_admins_success(self, backup_name: str, size_bytes: int, exit_code: int) -> None:
        ts = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M:%S")
        message = (
            "✅ **Резервная копия БД создана**\n\n"
            f"📄 Файл: `{backup_name}`\n"
            f"📦 Размер: {_format_size(size_bytes)}\n"
            f"🔚 Код выхода: {exit_code}\n"
            f"⏰ Время (UTC): {ts}"
        )
        await self._broadcast(message)

    async def _notify_admins_failure(self, backup_name: str, exit_code: int, err_text: str) -> None:
        snippet = (err_text[:500] + "…") if len(err_text) > 500 else err_text
        message = (
            "❌ **Бэкап не создан**\n\n"
            f"📄 Файл: `{backup_name}`\n"
            f"🔚 Код выхода: {exit_code}\n"
            f"📝 stderr: `{snippet or '<empty>'}`"
        )
        await self._broadcast(message)

    async def _broadcast(self, message: str) -> None:
        for admin_id in ADMIN_IDS:
            try:
                await self.bot.send_message(admin_id, message, parse_mode="Markdown")
            except Exception as e:
                logger.warning("Failed to notify admin %s: %s", admin_id, e)

    def start(self) -> None:
        self.scheduler.add_job(self.create_backup, "interval", hours=12)
        self.scheduler.start()
        logger.info("Backup scheduler started (every 12 hours)")
