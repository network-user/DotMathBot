from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in the .env file")

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{BASE_DIR / 'app' / 'data' / 'bot.db'}".replace("\\", "/"),
)
DB_PATH: Path = BASE_DIR / "app" / "data"

DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

ADMIN_IDS: list[int] = [
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
]

ADMIN_BACKUP_PASSWORD: str = os.getenv("ADMIN_BACKUP_PASSWORD", "secret_pass_123")
