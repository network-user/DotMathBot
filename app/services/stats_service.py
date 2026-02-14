from app.utils.helpers import get_accuracy_percentage
from app.database.db import get_user_stats, get_top_users
from app.locales import get_text


class StatsService:
    @staticmethod
    async def get_formatted_profile(telegram_id: int, lang: str = "ru") -> str:
        stats = await get_user_stats(telegram_id)
        if not stats:
            return get_text("profile_not_found", lang)

        accuracy = get_accuracy_percentage(stats.get("correct", 0), stats.get("total", 0))
        text = (
            get_text("profile_title", lang)
            + get_text("profile_stats", lang)
            + get_text("profile_correct", lang).format(n=stats.get("correct", 0))
            + get_text("profile_incorrect", lang).format(n=stats.get("incorrect", 0))
            + get_text("profile_total", lang).format(n=stats.get("total", 0))
            + get_text("profile_accuracy", lang).format(acc=accuracy)
            + get_text("profile_streaks", lang)
            + get_text("profile_current_streak", lang).format(n=stats.get("current_streak", 0))
            + get_text("profile_max_streak", lang).format(n=stats.get("max_streak", 0))
        )
        return text

    @staticmethod
    async def get_formatted_leaderboard(limit: int = 10, lang: str = "ru") -> str:
        top_users = await get_top_users(limit)
        if not top_users:
            return get_text("leaderboard_empty", lang)

        text = get_text("leaderboard_title", lang)
        anonymous = get_text("leaderboard_anonymous", lang)
        for idx, (user, streak) in enumerate(top_users, 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            name = user.first_name or user.username or anonymous
            text += f"{medal} {name}: {streak} days\n" if lang == "en" else f"{medal} {name}: {streak} дней\n"
        return text
