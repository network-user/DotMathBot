import asyncio
import logging

from app.config import DEBUG
from app.utils.logger import setup_logging
from app.bootstrap import setup_app, run_app

setup_logging(
    logs_dir="logs",
    log_level=logging.DEBUG if DEBUG else logging.INFO,
)

logger = logging.getLogger(__name__)


async def main() -> None:
    try:
        app = await setup_app()
        await run_app(app)
    except Exception as e:
        logger.critical("Critical error during bot startup: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
