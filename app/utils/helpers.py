from typing import Optional
from datetime import datetime, timedelta


def format_time(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")


def get_streak_status(last_training_date: Optional[datetime]) -> tuple[bool, int]:
    if not last_training_date:
        return False, 0

    today = datetime.now().date()
    last_date = last_training_date.date()
    days_diff = (today - last_date).days

    is_active = days_diff <= 1

    return is_active, days_diff


def parse_time_from_text(text: str) -> Optional[dict]:
    try:
        parts = text.strip().split(":")
        if len(parts) != 2:
            return None
        hours, minutes = int(parts[0]), int(parts[1])
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            return None
        return {"hours": hours, "minutes": minutes}
    except (ValueError, AttributeError):
        return None


def get_accuracy_percentage(correct: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round((correct / total) * 100, 1)


def format_stats(stats: dict) -> str:
    accuracy = get_accuracy_percentage(stats.get("correct", 0), stats.get("total", 0))

    text = (
        f"📊 Статистика\n\n"
        f"✅ Решено правильно: {stats.get('correct', 0)}\n"
        f"❌ Решено неправильно: {stats.get('incorrect', 0)}\n"
        f"📈 Точность: {accuracy}%\n"
        f"🔥 Серия дней: {stats.get('current_streak', 0)}\n"
        f"📅 Макс серия: {stats.get('max_streak', 0)}"
    )

    return text