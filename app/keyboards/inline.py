"""Inline keyboards. All callback_data values use typed factories from callbacks.py.

Keyboards here are pure builders — no I/O, no state. Handlers feed in the
state-dependent parameters (lang, daily_done flag, pagination offsets).
"""
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.keyboards.callbacks import (
    AdminCB,
    BackCB,
    LeaderboardCB,
    MenuCB,
    NotifCB,
    ProfileCB,
    TipsCB,
    TrainingCB,
)
from app.locales import get_text
from app.utils.constants import (
    Difficulty,
    NOTIFICATION_PRESETS,
    NotificationPreset,
    TrainingMode,
)


class InlineKeyboards:
    @staticmethod
    def main_menu(lang: str = "ru", daily_done: bool = False) -> InlineKeyboardMarkup:
        daily_label = get_text("btn_daily_challenge", lang)
        if daily_done:
            daily_label += " ✅"
        buttons = [
            [
                InlineKeyboardButton(
                    text=daily_label, callback_data=MenuCB(action="daily").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("btn_start_training", lang),
                    callback_data=MenuCB(action="training").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("btn_my_profile", lang),
                    callback_data=MenuCB(action="profile").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("btn_notifications", lang),
                    callback_data=MenuCB(action="notifications").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("btn_leaderboard", lang),
                    callback_data=MenuCB(action="leaderboard").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("btn_tips", lang),
                    callback_data=MenuCB(action="tips").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("btn_lang_ru", lang),
                    callback_data=MenuCB(action="lang_ru").pack(),
                ),
                InlineKeyboardButton(
                    text=get_text("btn_lang_en", lang),
                    callback_data=MenuCB(action="lang_en").pack(),
                ),
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def admin_main_menu(lang: str = "ru") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=get_text("admin_btn_stats", lang),
                        callback_data=AdminCB(action="stats").pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=get_text("admin_btn_users", lang),
                        callback_data=AdminCB(action="users", page=0).pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=get_text("admin_btn_backup", lang),
                        callback_data=AdminCB(action="backup").pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=get_text("admin_btn_download_backup", lang),
                        callback_data=AdminCB(action="download").pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=get_text("btn_back_to_menu", lang),
                        callback_data=BackCB(action="menu").pack(),
                    )
                ],
            ]
        )

    @staticmethod
    def admin_users_list(offset: int, has_next: bool, lang: str = "ru") -> InlineKeyboardMarkup:
        nav_row = []
        if offset > 0:
            nav_row.append(
                InlineKeyboardButton(
                    text=get_text("btn_back", lang),
                    callback_data=AdminCB(action="users", page=max(0, offset - 10)).pack(),
                )
            )
        if has_next:
            nav_row.append(
                InlineKeyboardButton(
                    text=get_text("btn_next", lang),
                    callback_data=AdminCB(action="users", page=offset + 10).pack(),
                )
            )

        buttons = []
        if nav_row:
            buttons.append(nav_row)
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_text("admin_btn_back_to_main", lang),
                    callback_data=AdminCB(action="main").pack(),
                )
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def difficulty_selection(lang: str = "ru") -> InlineKeyboardMarkup:
        keys = {
            Difficulty.EASY: "difficulty_easy",
            Difficulty.MEDIUM: "difficulty_medium",
            Difficulty.HARD: "difficulty_hard",
        }
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_text(keys[d], lang),
                    callback_data=TrainingCB(action="difficulty", difficulty=d.value).pack(),
                )
            ]
            for d in Difficulty
        ]
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_text("btn_back", lang),
                    callback_data=BackCB(action="menu").pack(),
                )
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def mode_selection(lang: str = "ru") -> InlineKeyboardMarkup:
        keys = {
            TrainingMode.CHOOSE_ANSWER: "mode_choose",
            TrainingMode.MULTIPLICATION_ONLY: "mode_mult",
            TrainingMode.DIVISION_ONLY: "mode_div",
            TrainingMode.MIXED: "mode_mixed",
            TrainingMode.ADDITION_ONLY: "mode_add",
            TrainingMode.SUBTRACTION_ONLY: "mode_sub",
            TrainingMode.DIVISION_REMAINDER: "mode_div_rem",
            TrainingMode.POWER_ONLY: "mode_pow",
            TrainingMode.SQRT_ONLY: "mode_sqrt",
        }
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_text(keys[m], lang),
                    callback_data=TrainingCB(action="mode", mode=m.value).pack(),
                )
            ]
            for m in TrainingMode
        ]
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_text("btn_back", lang),
                    callback_data=BackCB(action="menu").pack(),
                )
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def training_answer_variants(
        variants: list[tuple[int, bool]], problem_idx: int, lang: str = "ru"
    ) -> InlineKeyboardMarkup:
        # Variants in pairs of two for a 2-column dense layout.
        rows: list[list[InlineKeyboardButton]] = []
        row: list[InlineKeyboardButton] = []
        for answer, _ in variants:
            row.append(
                InlineKeyboardButton(
                    text=str(answer),
                    callback_data=TrainingCB(
                        action="answer", idx=problem_idx, answer=answer
                    ).pack(),
                )
            )
            if len(row) == 2:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
        rows.append(
            [
                InlineKeyboardButton(
                    text=get_text("btn_exit_training", lang),
                    callback_data=TrainingCB(action="exit").pack(),
                )
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=rows)

    @staticmethod
    def training_type_controls(lang: str = "ru") -> InlineKeyboardMarkup:
        """Single skip + exit row for typed-answer mode."""
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=get_text("btn_skip", lang),
                        callback_data=TrainingCB(action="skip").pack(),
                    ),
                    InlineKeyboardButton(
                        text=get_text("btn_exit_training", lang),
                        callback_data=TrainingCB(action="exit").pack(),
                    ),
                ]
            ]
        )

    @staticmethod
    def session_result(
        has_mistakes: bool, lang: str = "ru", session_kind: str = "normal"
    ) -> InlineKeyboardMarkup:
        """Post-session screen.

        Normal/retry sessions get [retry mistakes?][new][menu].
        Daily session gets [top of day][menu].
        """
        buttons: list[list[InlineKeyboardButton]] = []
        if session_kind == "daily":
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=get_text("btn_daily_leaderboard", lang),
                        callback_data=LeaderboardCB(action="page", mode="daily", page=0).pack(),
                    )
                ]
            )
        else:
            if has_mistakes:
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=get_text("btn_retry_mistakes", lang),
                            callback_data=TrainingCB(action="retry_mistakes").pack(),
                        )
                    ]
                )
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=get_text("btn_new_training", lang),
                        callback_data=MenuCB(action="training").pack(),
                    )
                ]
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_text("btn_back_to_menu", lang),
                    callback_data=BackCB(action="menu").pack(),
                )
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def daily_already_done(lang: str = "ru") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=get_text("btn_daily_leaderboard", lang),
                        callback_data=LeaderboardCB(action="page", mode="daily", page=0).pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=get_text("btn_back_to_menu", lang),
                        callback_data=BackCB(action="menu").pack(),
                    )
                ],
            ]
        )

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
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_text(preset_keys[p], lang),
                    callback_data=NotifCB(action="select", preset=p.value).pack(),
                )
            ]
            for p in NotificationPreset
        ]
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_text("btn_back", lang),
                    callback_data=BackCB(action="menu").pack(),
                )
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def cancel_custom_time(lang: str = "ru") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=get_text("btn_cancel", lang),
                        callback_data=NotifCB(action="cancel_custom").pack(),
                    )
                ]
            ]
        )

    @staticmethod
    def tips_menu(lang: str = "ru") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=get_text("tips_multiplication_btn", lang),
                        callback_data=TipsCB(action="multiplication").pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=get_text("tips_division_btn", lang),
                        callback_data=TipsCB(action="division").pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=get_text("tips_general_btn", lang),
                        callback_data=TipsCB(action="general").pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=get_text("btn_back", lang),
                        callback_data=BackCB(action="menu").pack(),
                    )
                ],
            ]
        )

    @staticmethod
    def back_to_menu(lang: str = "ru", show_in_top: bool = True) -> InlineKeyboardMarkup:
        toggle_key = "btn_toggle_top_hide" if show_in_top else "btn_toggle_top_show"
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=get_text(toggle_key, lang),
                        callback_data=ProfileCB(action="toggle_top").pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=get_text("btn_back_to_menu", lang),
                        callback_data=BackCB(action="menu").pack(),
                    )
                ],
            ]
        )

    @staticmethod
    def back_only(lang: str = "ru") -> InlineKeyboardMarkup:
        """Bare 'back to menu' keyboard — no privacy toggle (for non-profile screens)."""
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=get_text("btn_back_to_menu", lang),
                        callback_data=BackCB(action="menu").pack(),
                    )
                ]
            ]
        )

    @staticmethod
    def leaderboard_mode_choice(
        lang: str = "ru",
        mode: str | None = None,
        offset: int = 0,
        has_next: bool = False,
    ) -> InlineKeyboardMarkup:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_text("btn_leaderboard_streak", lang),
                    callback_data=LeaderboardCB(action="page", mode="streak", page=0).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("btn_leaderboard_solved", lang),
                    callback_data=LeaderboardCB(action="page", mode="solved", page=0).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("btn_leaderboard_accuracy", lang),
                    callback_data=LeaderboardCB(action="page", mode="accuracy", page=0).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("btn_leaderboard_weighted", lang),
                    callback_data=LeaderboardCB(action="page", mode="weighted", page=0).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("btn_leaderboard_daily", lang),
                    callback_data=LeaderboardCB(action="page", mode="daily", page=0).pack(),
                )
            ],
        ]

        if mode:
            nav_row = []
            if offset > 0:
                nav_row.append(
                    InlineKeyboardButton(
                        text=get_text("btn_back", lang),
                        callback_data=LeaderboardCB(
                            action="page", mode=mode, page=max(0, offset - 10)
                        ).pack(),
                    )
                )
            if has_next:
                nav_row.append(
                    InlineKeyboardButton(
                        text=get_text("btn_next", lang),
                        callback_data=LeaderboardCB(
                            action="page", mode=mode, page=offset + 10
                        ).pack(),
                    )
                )
            if nav_row:
                buttons.append(nav_row)

        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_text("btn_back_to_menu", lang),
                    callback_data=BackCB(action="menu").pack(),
                )
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=buttons)
