from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in the .env file")

DATABASE_URL: str = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set. Example: "
        "postgresql+asyncpg://dotmath:password@localhost:5432/dotmath"
    )

# Optional Redis for FSM persistence. When unset, the bot falls back to
# MemoryStorage (FSM state is lost on restart — fine for local dev, not for
# prod, since users mid-training would get stuck). Compose sets this to
# ``redis://redis:6379/0``.
REDIS_URL: str = os.getenv("REDIS_URL", "").strip()

# Filesystem path used by services like BackupService and Alembic for ensuring
# the data directory exists. Not used for DB connection any more.
DB_PATH: Path = BASE_DIR / "app" / "data"

DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

ADMIN_IDS: list[int] = [
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
]

ADMIN_BACKUP_PASSWORD: str = os.getenv("ADMIN_BACKUP_PASSWORD", "")
if not ADMIN_BACKUP_PASSWORD:
    raise ValueError("ADMIN_BACKUP_PASSWORD is not set in the .env file")
