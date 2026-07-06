from typing import Optional
from datetime import datetime, timedelta, timezone


# Legacy Telegram "Markdown" metacharacters that can open an entity or a link.
# Untrusted text (user display names) must have these escaped before it lands in
# a parse_mode="Markdown" message: a crafted first_name like ``[x](http://phish)``
# would otherwise inject a clickable link into shared messages (the leaderboard),
# and an unbalanced `` ` ``/``*``/``_`` breaks rendering (Telegram HTTP 400).
_MD_SPECIAL = ("_", "*", "`", "[")


def escape_md(text: Optional[str]) -> str:
    """Escape legacy-Markdown metacharacters in untrusted text.

    Backslash is escaped first so an attacker can't neutralise our escape by
    prefixing one (``\\[`` would re-open the link otherwise). Covers the full
    set Telegram's legacy ``Markdown`` parser treats as special. New code should
    prefer parse_mode="HTML" with ``html.escape`` or MarkdownV2.
    """
    if not text:
        return ""
    text = text.replace("\\", "\\\\")
    for ch in _MD_SPECIAL:
        text = text.replace(ch, "\\" + ch)
    return text


def format_time(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")


def get_streak_status(last_training_date: Optional[datetime]) -> tuple[bool, int]:
    if not last_training_date:
        return False, 0

    today = datetime.now(timezone.utc).date()
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