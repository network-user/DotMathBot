from app.utils.helpers import get_accuracy_percentage
from app.database.db import (
    get_user_stats,
    get_top_users,
    get_top_users_by_streak,
    get_top_users_by_solved,
    get_top_users_by_accuracy,
    get_top_users_by_weighted,
    get_user_rank,
)
from app.locales import get_text


class StatsService:
    @staticmethod
    @staticmethod
    async def get_formatted_profile(telegram_id: int, lang: str = "ru") -> str:
        stats = await get_user_stats(telegram_id)
        if not stats:
            return get_text("profile_not_found", lang)

        accuracy = get_accuracy_percentage(stats.get("correct", 0), stats.get("total", 0))
        show_in_top_status = "✅ Да" if stats.get("show_in_top", True) else "❌ Нет"
        
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
            + f"\n\n👤 **Показывать в топе:** {show_in_top_status}"
        )
        return text

    @staticmethod
    async def get_formatted_leaderboard(
        limit: int = 10, offset: int = 0, lang: str = "ru", mode: str = "streak", telegram_id: int | None = None
    ) -> tuple[str, bool]:
        """Форматирует топ по выбранному режиму: streak | solved | accuracy | weighted."""
        if mode == "streak":
            top_data, has_next = await get_top_users_by_streak(limit, offset)
            title_key = "leaderboard_title_streak"
            row_key = "leaderboard_row_days"
        elif mode == "solved":
            top_data, has_next = await get_top_users_by_solved(limit, offset)
            title_key = "leaderboard_title_solved"
            row_key = "leaderboard_row_solved"
        elif mode == "accuracy":
            top_data, has_next = await get_top_users_by_accuracy(limit, offset)
            title_key = "leaderboard_title_accuracy"
            row_key = "leaderboard_row_accuracy"
        elif mode == "weighted":
            top_data, has_next = await get_top_users_by_weighted(limit, offset)
            title_key = "leaderboard_title_weighted"
            row_key = "leaderboard_row_weighted"
        else:
            top_data, has_next = await get_top_users_by_streak(limit, offset)
            title_key = "leaderboard_title_streak"
            row_key = "leaderboard_row_days"

        if not top_data and offset == 0:
            return get_text("leaderboard_empty", lang), False
        
        if not top_data:
            return "Конец списка.", False

        text = get_text(title_key, lang)
        text += "━" * 15 + "\n"
        text += get_text("leaderboard_legend", lang)
        
        anonymous = get_text("leaderboard_anonymous", lang)
        hidden_label = "🕵️ Скрыто" if lang == "ru" else "🕵️ Hidden"

        for i, (user, value, diff) in enumerate(top_data, 1):
            idx = offset + i
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"**{idx}.**"
            
            # Логика скрытия имени
            if not user.show_in_top:
                name = f"_{hidden_label}_"
            else:
                name = user.first_name or user.username or anonymous
            
            text += get_text(row_key, lang).format(
                medal=medal,
                name=name,
                value=value,
                easy=diff.get("easy", 0),
                medium=diff.get("medium", 0),
                hard=diff.get("hard", 0),
            )

        if telegram_id is not None:
            rank, total = await get_user_rank(telegram_id, mode)
            if rank is not None and total > 0:
                text += "━" * 15 + "\n"
                text += get_text("leaderboard_your_place", lang).format(rank=rank, total=total)

        return text, has_next

    @staticmethod
    async def get_leaderboard_choose_mode_text(lang: str = "ru") -> str:
        return get_text("leaderboard_choose_mode", lang)
