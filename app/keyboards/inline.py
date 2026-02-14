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
    def back_to_menu(lang: str = "ru") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=get_text("btn_back_to_menu", lang),
                        callback_data="back_to_menu",
                    )
                ]
            ]
        )
