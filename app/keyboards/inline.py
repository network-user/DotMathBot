from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.utils.constants import (
    Difficulty,
    DIFFICULTY_CONFIG,
    TrainingMode,
    TRAINING_MODE_CONFIG,
    NotificationPreset,
    NOTIFICATION_PRESETS,
)
from app.locales import get_text


class InlineKeyboards:
    @staticmethod
    def main_menu(lang: str = "ru") -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text=get_text("btn_start_training", lang), callback_data="start_training")],
            [InlineKeyboardButton(text=get_text("btn_my_profile", lang), callback_data="show_profile")],
            [InlineKeyboardButton(text=get_text("btn_notifications", lang), callback_data="settings_notifications")],
            [InlineKeyboardButton(text=get_text("btn_leaderboard", lang), callback_data="show_leaderboard")],
            [InlineKeyboardButton(text=get_text("btn_tips", lang), callback_data="show_tips")],
            [
                InlineKeyboardButton(text=get_text("btn_lang_ru", lang), callback_data="lang_ru"),
                InlineKeyboardButton(text=get_text("btn_lang_en", lang), callback_data="lang_en"),
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def admin_main_menu() -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_users:0")],
            [InlineKeyboardButton(text="💾 Создать бэкап", callback_data="admin_backup")],
            [InlineKeyboardButton(text="📂 Скачать бэкап", callback_data="admin_download_backup")],
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_menu")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def admin_users_list(offset: int, has_next: bool) -> InlineKeyboardMarkup:
        buttons = []
        nav_buttons = []
        if offset > 0:
            nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_users:{max(0, offset-10)}"))
        if has_next:
            nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"admin_users:{offset+10}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
            
        buttons.append([InlineKeyboardButton(text="🔙 В админ-меню", callback_data="admin_main")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def difficulty_selection(lang: str = "ru") -> InlineKeyboardMarkup:
        keys = {
            Difficulty.EASY: "difficulty_easy",
            Difficulty.MEDIUM: "difficulty_medium",
            Difficulty.HARD: "difficulty_hard",
        }
        buttons = []
        for difficulty in Difficulty:
            text = get_text(keys[difficulty], lang)
            buttons.append([InlineKeyboardButton(text=text, callback_data=f"difficulty_{difficulty.value}")])
        buttons.append([InlineKeyboardButton(text=get_text("btn_back", lang), callback_data="back_to_menu")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def mode_selection(lang: str = "ru") -> InlineKeyboardMarkup:
        keys = {
            TrainingMode.CHOOSE_ANSWER: "mode_choose",
            TrainingMode.MULTIPLICATION_ONLY: "mode_mult",
            TrainingMode.DIVISION_ONLY: "mode_div",
            TrainingMode.MIXED: "mode_mixed",
        }
        buttons = []
        for mode in TrainingMode:
            text = get_text(keys[mode], lang)
            buttons.append([InlineKeyboardButton(text=text, callback_data=f"mode_{mode.value}")])
        buttons.append([InlineKeyboardButton(text=get_text("btn_back", lang), callback_data="back_to_menu")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def training_answer_variants(
        variants: list[tuple[int, bool]], problem_idx: int, lang: str = "ru"
    ) -> InlineKeyboardMarkup:
        buttons = []
        for answer, _ in variants:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=str(answer),
                        callback_data=f"answer_{problem_idx}_{answer}",
                    )
                ]
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_text("btn_abort_training_full", lang),
                    callback_data="abort_training",
                )
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def training_continue(lang: str = "ru") -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text=get_text("btn_next", lang), callback_data="next_problem")],
            [
                InlineKeyboardButton(
                    text=get_text("btn_abort_training_full", lang),
                    callback_data="finish_training",
                )
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def problem_actions(problem_idx: int, total: int, lang: str = "ru") -> InlineKeyboardMarkup:
        buttons = [
            [
                InlineKeyboardButton(text="💡 Подсказка", callback_data=f"hint_{problem_idx}"),
                InlineKeyboardButton(text="📖 Решение", callback_data=f"solution_{problem_idx}"),
            ],
            [InlineKeyboardButton(text=f"Пример {problem_idx}/{total}", callback_data="info")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def notification_preset_selection(lang: str = "ru") -> InlineKeyboardMarkup:
        preset_keys = {
            NotificationPreset.MORNING: "notify_preset_morning",
            NotificationPreset.LUNCH: "notify_preset_lunch",
            NotificationPreset.EVENING: "notify_preset_evening",
            NotificationPreset.THREE_TIMES: "notify_preset_three",
            NotificationPreset.CUSTOM: "notify_preset_custom",
            NotificationPreset.DISABLED: "notify_preset_disabled",
        }
        buttons = []
        for preset in NotificationPreset:
            text = get_text(preset_keys[preset], lang)
            buttons.append(
                [InlineKeyboardButton(text=text, callback_data=f"notify_preset_{preset.value}")]
            )
        buttons.append([InlineKeyboardButton(text=get_text("btn_back", lang), callback_data="back_to_menu")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def cancel_custom_time(lang: str = "ru") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=get_text("btn_cancel", lang),
                    callback_data="cancel_custom_time"
                )]
            ]
        )

    @staticmethod
    def tips_menu(lang: str = "ru") -> InlineKeyboardMarkup:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_text("tips_multiplication_btn", lang),
                    callback_data="tips_multiplication",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("tips_division_btn", lang),
                    callback_data="tips_division",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("tips_general_btn", lang),
                    callback_data="tips_general",
                )
            ],
            [InlineKeyboardButton(text=get_text("btn_back", lang), callback_data="back_to_menu")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def back_to_menu(lang: str = "ru", show_in_top: bool = True) -> InlineKeyboardMarkup:
        toggle_text = "👤 Скрыть имя в топе" if show_in_top else "👤 Показать имя в топе"
        toggle_data = "toggle_top_privacy"
        
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=toggle_text, callback_data=toggle_data)],
                [
                    InlineKeyboardButton(
                        text=get_text("btn_back_to_menu", lang),
                        callback_data="back_to_menu",
                    )
                ]
            ]
        )

    @staticmethod
    def leaderboard_mode_choice(lang: str = "ru", mode: str | None = None, offset: int = 0, has_next: bool = False) -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text=get_text("btn_leaderboard_streak", lang), callback_data="leaderboard_streak:0")],
            [InlineKeyboardButton(text=get_text("btn_leaderboard_solved", lang), callback_data="leaderboard_solved:0")],
            [InlineKeyboardButton(text=get_text("btn_leaderboard_accuracy", lang), callback_data="leaderboard_accuracy:0")],
            [InlineKeyboardButton(text=get_text("btn_leaderboard_weighted", lang), callback_data="leaderboard_weighted:0")],
        ]
        
        if mode:
            nav_row = []
            if offset > 0:
                nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"leaderboard_{mode}:{max(0, offset-10)}"))
            if has_next:
                nav_row.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"leaderboard_{mode}:{offset+10}"))
            
            if nav_row:
                buttons.append(nav_row)

        buttons.append([InlineKeyboardButton(text=get_text("btn_back_to_menu", lang), callback_data="back_to_menu")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)
