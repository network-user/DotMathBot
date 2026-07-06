"""PostgreSQL backup service.

Spawns `pg_dump` via asyncio subprocess to produce a custom-format dump
(`.dump`) which can be restored with `pg_restore`. Runs every 12 hours,
retains the 20 most recent files, and notifies admins (with file size +
exit code) after each run.
"""
from __future__ import annotations

import asyncio
import base64
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit, urlunsplit

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import ADMIN_BACKUP_PASSWORD, ADMIN_IDS, DATABASE_URL, DB_PATH

logger = logging.getLogger(__name__)

BACKUP_RETENTION = 20
BACKUP_FILENAME_PREFIX = "bot_backup_"
# Dumps are encrypted at rest (and in transit over Telegram), so the artifact is
# a ``.dump.enc`` blob; decrypt with ``python -m app.services.backup_service``.
BACKUP_FILENAME_SUFFIX = ".dump.enc"

_ENC_MAGIC = b"DMB1"           # DotMathBot encrypted-backup format marker, v1
_ENC_SALT_LEN = 16
_ENC_KDF_ITERATIONS = 200_000


def _derive_fernet_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet key from the backup password + per-file salt (PBKDF2-HMAC-SHA256)."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=_ENC_KDF_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def _encrypt_file(src: Path, dst: Path, password: str) -> None:
    """Encrypt ``src`` into ``dst`` (magic || salt || Fernet token). AES-128-CBC + HMAC via Fernet."""
    salt = os.urandom(_ENC_SALT_LEN)
    token = Fernet(_derive_fernet_key(password, salt)).encrypt(src.read_bytes())
    dst.write_bytes(_ENC_MAGIC + salt + token)


def decrypt_backup(src: Path, dst: Path, password: str) -> None:
    """Decrypt a ``.dump.enc`` backup produced by this service back to a pg_restore-able dump."""
    blob = src.read_bytes()
    if blob[:len(_ENC_MAGIC)] != _ENC_MAGIC:
        raise ValueError("Not a DotMathBot encrypted backup (bad magic header)")
    salt = blob[len(_ENC_MAGIC):len(_ENC_MAGIC) + _ENC_SALT_LEN]
    token = blob[len(_ENC_MAGIC) + _ENC_SALT_LEN:]
    data = Fernet(_derive_fernet_key(password, salt)).decrypt(token)
    dst.write_bytes(data)


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
            os.chmod(self.backups_dir, 0o700)  # backups hold full PII: owner-only
        except OSError as e:
            logger.error("Could not create backups directory %s: %s", self.backups_dir, e)

    async def create_backup(self) -> Path | None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_name = f"{BACKUP_FILENAME_PREFIX}{timestamp}{BACKUP_FILENAME_SUFFIX}"
        backup_path = self.backups_dir / backup_name
        plain_path = backup_path.with_suffix("")  # strip .enc -> temporary plaintext dump

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
            f"--file={plain_path}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        stdout, stderr = await proc.communicate()
        exit_code = proc.returncode or 0

        if exit_code != 0 or not plain_path.exists():
            err_text = _scrub_secrets(
                (stderr or b"").decode("utf-8", errors="replace").strip()
            )
            logger.error(
                "pg_dump failed (exit=%s): %s", exit_code, err_text or "<no stderr>"
            )
            plain_path.unlink(missing_ok=True)
            await self._notify_admins_failure(backup_name, exit_code, err_text)
            return None

        # Encrypt at rest and in transit: the dump holds all user PII, so the
        # plaintext never leaves this function (temp file removed in finally).
        try:
            _encrypt_file(plain_path, backup_path, ADMIN_BACKUP_PASSWORD)
            os.chmod(backup_path, 0o600)
        except Exception:
            logger.exception("Backup encryption failed")
            backup_path.unlink(missing_ok=True)
            await self._notify_admins_failure(backup_name, exit_code, "encryption failed")
            return None
        finally:
            plain_path.unlink(missing_ok=True)

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


def _decrypt_cli() -> None:
    """Restore helper: decrypt a .dump.enc backup to a pg_restore-able .dump.

    Usage: python -m app.services.backup_service <backup.dump.enc> [out.dump]
    Password is read from ADMIN_BACKUP_PASSWORD or prompted interactively.
    """
    import getpass
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m app.services.backup_service <backup.dump.enc> [out.dump]")
        raise SystemExit(2)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix("")  # drop .enc
    password = os.environ.get("ADMIN_BACKUP_PASSWORD") or getpass.getpass("Backup password: ")
    decrypt_backup(src, dst, password)
    print(f"Decrypted -> {dst}")


if __name__ == "__main__":
    _decrypt_cli()
