"""Logs are written to console and to files with automatic rotation."""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging(
        logs_dir: str | Path = "logs",
        log_level: int = logging.INFO,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
) -> None:
    logs_path = Path(logs_dir)
    logs_path.mkdir(parents=True, exist_ok=True)

    console_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    file_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    console_formatter = ColoredFormatter(console_format, date_format)
    file_formatter = logging.Formatter(file_format, date_format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)

    general_file = logs_path / "bot.log"
    general_handler = RotatingFileHandler(
        general_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    general_handler.setLevel(logging.INFO)
    general_handler.setFormatter(file_formatter)

    error_file = logs_path / "errors.log"
    error_handler = RotatingFileHandler(
        error_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    debug_file = logs_path / "debug.log"
    debug_handler = RotatingFileHandler(
        debug_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(file_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
    root_logger.addHandler(general_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(debug_handler)

    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Logging configured")
    logger.info("Logs directory: %s", logs_path.absolute())
    logger.info("Console level: %s", logging.getLevelName(log_level))
    logger.info("=" * 60)


class ColoredFormatter(logging.Formatter):

    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET": "\033[0m",       # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        levelname = record.levelname
        if levelname in self.COLORS:
            levelname_color = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            record.levelname = levelname_color
        return super().format(record)
