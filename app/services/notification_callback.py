import logging
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

logger = logging.getLogger(__name__)


async def send_training_reminder(bot: Bot, telegram_id: int) -> None:
    logger.info(f"Sending reminder to telegram_id={telegram_id}")

    text = (
        "🎯 **Время тренировки!**\n\n"
        "Давай потренируем устный счёт!\n"
        "Это займёт всего несколько минут 💪\n\n"
        "Нажми /train для начала тренировки."
    )

    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
            parse_mode="Markdown"
        )
        logger.info(f"Reminder sent successfully to telegram_id={telegram_id}")

    except TelegramForbiddenError:
        logger.warning(f"User {telegram_id} blocked the bot")

    except TelegramBadRequest as e:
        logger.error(f"Failed to send reminder to {telegram_id}: {e}")

    except Exception as e:
        logger.error(f"Unexpected error sending reminder to {telegram_id}: {e}", exc_info=True)
