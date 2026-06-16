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
    SettingsCB,
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

# Modes shown without "More…" expansion. Order = display order.
_MODE_PRIMARY: tuple[TrainingMode, ...] = (
    TrainingMode.MULTIPLICATION_ONLY,
    TrainingMode.DIVISION_ONLY,
    TrainingMode.MIXED,
    TrainingMode.CHOOSE_ANSWER,
)
# Modes hidden behind "More…".
_MODE_SECONDARY: tuple[TrainingMode, ...] = (
    TrainingMode.ADDITION_ONLY,
    TrainingMode.SUBTRACTION_ONLY,
    TrainingMode.DIVISION_REMAINDER,
    TrainingMode.POWER_ONLY,
    TrainingMode.SQRT_ONLY,
)

_MODE_LABEL_KEYS: dict[TrainingMode, str] = {
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


def mode_label(mode: TrainingMode | str | None, lang: str) -> str:
    """Resolve a TrainingMode (or its string value) to its localized label.

    Returns "" for None, unknown strings, or anything else that doesn't map
    to a known mode — callers can treat empty as "skip rendering this row".
    """
    if mode is None:
        return ""
    if isinstance(mode, TrainingMode):
        key = _MODE_LABEL_KEYS.get(mode)
        return get_text(key, lang) if key else ""
    if isinstance(mode, str):
        try:
            return get_text(_MODE_LABEL_KEYS[TrainingMode(mode)], lang)
        except (ValueError, KeyError):
            return ""
    return ""


_DIFFICULTY_LABEL_KEYS: dict[Difficulty, str] = {
    Difficulty.EASY: "difficulty_easy",
    Difficulty.MEDIUM: "difficulty_medium",
    Difficulty.HARD: "difficulty_hard",
}


def difficulty_label(difficulty: Difficulty | str | None, lang: str) -> str:
    """Resolve a Difficulty (or its string value) to its localized label."""
    if difficulty is None:
        return ""
    if isinstance(difficulty, Difficulty):
        return get_text(_DIFFICULTY_LABEL_KEYS[difficulty], lang)
    if isinstance(difficulty, str):
        try:
            return get_text(_DIFFICULTY_LABEL_KEYS[Difficulty(difficulty)], lang)
        except (ValueError, KeyError):
            return ""
    return ""


class InlineKeyboards:
    @staticmethod
    def main_menu(
        lang: str = "ru",
        daily_done: bool = False,
        favorite_mode: str | None = None,
        favorite_difficulty: str | None = None,
    ) -> InlineKeyboardMarkup:
        """Compact 2-column main menu.

        Top row is a full-width Quick Start when ``favorite_mode`` is set;
        otherwise the menu starts directly with Training + Daily. Language
        toggles moved to Settings to declutter this screen.
        """
        daily_label = get_text("btn_daily_challenge", lang)
        if daily_done:
            daily_label += " ✅"

        rows: list[list[InlineKeyboardButton]] = []
        mode_text = mode_label(favorite_mode, lang) if favorite_mode else ""
        if mode_text:
            diff_text = difficulty_label(favorite_difficulty or "medium", lang)
            combined = f"{diff_text} {mode_text}".strip()
            fav_label = get_text("btn_quick_start", lang).format(mode=combined)
            rows.append(
                [
                    InlineKeyboardButton(
                        text=fav_label,
                        callback_data=MenuCB(action="quick_start").pack(),
                    )
                ]
            )
        rows.append(
            [
                InlineKeyboardButton(
                    text=get_text("btn_start_training", lang),
                    callback_data=MenuCB(action="training").pack(),
                ),
                InlineKeyboardButton(
                    text=daily_label, callback_data=MenuCB(action="daily").pack()
                ),
            ]
        )
        rows.append(
            [
                InlineKeyboardButton(
                    text=get_text("btn_my_profile", lang),
                    callback_data=MenuCB(action="profile").pack(),
                ),
                InlineKeyboardButton(
                    text=get_text("btn_leaderboard", lang),
                    callback_data=MenuCB(action="leaderboard").pack(),
                ),
            ]
        )
        rows.append(
            [
                InlineKeyboardButton(
                    text=get_text("btn_tips", lang),
                    callback_data=MenuCB(action="tips").pack(),
                ),
                InlineKeyboardButton(
                    text=get_text("btn_settings", lang),
                    callback_data=MenuCB(action="settings").pack(),
                ),
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=rows)

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
    def mode_selection(lang: str = "ru", expanded: bool = False) -> InlineKeyboardMarkup:
        """Two-level mode picker.

        Collapsed (default): the 3 main modes + typed-answer + "More…".
        Expanded: also shows +/−/remainder/power/sqrt and a "Hide" toggle.
        """
        shown: tuple[TrainingMode, ...] = _MODE_PRIMARY
        if expanded:
            shown = _MODE_PRIMARY + _MODE_SECONDARY

        buttons: list[list[InlineKeyboardButton]] = [
            [
                InlineKeyboardButton(
                    text=get_text(_MODE_LABEL_KEYS[m], lang),
                    callback_data=TrainingCB(action="mode", mode=m.value).pack(),
                )
            ]
            for m in shown
        ]
        toggle_key = "btn_mode_less" if expanded else "btn_mode_more"
        toggle_action = "mode_less" if expanded else "mode_more"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_text(toggle_key, lang),
                    callback_data=TrainingCB(action=toggle_action).pack(),
                )
            ]
        )
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
    def settings_menu(
        lang: str = "ru",
        favorite_mode: str | None = None,
        favorite_difficulty: str | None = None,
        show_in_top: bool = False,
    ) -> InlineKeyboardMarkup:
        """Hub for all per-user preferences (favorite, language, etc.)."""
        mode_text = mode_label(favorite_mode, lang)
        if mode_text:
            diff_text = difficulty_label(favorite_difficulty or "medium", lang)
            fav_text = get_text("btn_settings_favorite", lang).format(
                mode=f"{diff_text} {mode_text}".strip()
            )
        else:
            fav_text = get_text("btn_settings_favorite_unset", lang)

        privacy_key = "btn_settings_privacy_hide" if show_in_top else "btn_settings_privacy_show"

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=fav_text,
                        callback_data=SettingsCB(action="favorite_open").pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=get_text("btn_settings_notifications", lang),
                        callback_data=MenuCB(action="notifications").pack(),
                    ),
                    InlineKeyboardButton(
                        text=get_text(privacy_key, lang),
                        callback_data=ProfileCB(action="toggle_top").pack(),
                    ),
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
                [
                    InlineKeyboardButton(
                        text=get_text("btn_back_to_menu", lang),
                        callback_data=BackCB(action="menu").pack(),
                    )
                ],
            ]
        )

    @staticmethod
    def favorite_difficulty_selection(
        lang: str = "ru",
        current_difficulty: str | None = None,
    ) -> InlineKeyboardMarkup:
        """Step 1 of the favorite picker — pick difficulty.

        Click feeds ``SettingsCB(action="favorite_difficulty", difficulty=X)``
        which then renders the mode picker with X carried in callback data.
        """
        buttons: list[list[InlineKeyboardButton]] = []
        for d in Difficulty:
            label = get_text(_DIFFICULTY_LABEL_KEYS[d], lang)
            if current_difficulty == d.value:
                label = f"• {label} •"
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=label,
                        callback_data=SettingsCB(
                            action="favorite_difficulty", difficulty=d.value
                        ).pack(),
                    )
                ]
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_text("btn_back_to_settings", lang),
                    callback_data=SettingsCB(action="open").pack(),
                )
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def favorite_mode_selection(
        lang: str = "ru",
        current_mode: str | None = None,
        expanded: bool = False,
        difficulty: str | None = None,
    ) -> InlineKeyboardMarkup:
        """Step 2 of the favorite picker — pick the mode under ``difficulty``.

        Every callback carries ``difficulty`` so expand/collapse don't lose
        the user's choice from step 1.
        """
        shown: tuple[TrainingMode, ...] = _MODE_PRIMARY
        if expanded:
            shown = _MODE_PRIMARY + _MODE_SECONDARY

        buttons: list[list[InlineKeyboardButton]] = []
        for m in shown:
            label = get_text(_MODE_LABEL_KEYS[m], lang)
            if current_mode == m.value:
                label = f"• {label} •"
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=label,
                        callback_data=SettingsCB(
                            action="favorite_set",
                            mode=m.value,
                            difficulty=difficulty,
                        ).pack(),
                    )
                ]
            )
        toggle_key = "btn_mode_less" if expanded else "btn_mode_more"
        toggle_action = "favorite_less" if expanded else "favorite_more"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_text(toggle_key, lang),
                    callback_data=SettingsCB(
                        action=toggle_action, difficulty=difficulty
                    ).pack(),
                )
            ]
        )
        if current_mode:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=get_text("btn_favorite_clear", lang),
                        callback_data=SettingsCB(action="favorite_clear").pack(),
                    )
                ]
            )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_text("btn_back_to_settings", lang),
                    callback_data=SettingsCB(action="open").pack(),
                )
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def training_answer_variants(
        variants: list[tuple[int, bool]], problem_idx: int, lang: str = "ru"
    ) -> InlineKeyboardMarkup:
        """One variant per row — full-width buttons are easier to tap."""
        rows: list[list[InlineKeyboardButton]] = [
            [
                InlineKeyboardButton(
                    text=str(answer),
                    callback_data=TrainingCB(
                        action="answer", idx=problem_idx, answer=answer
                    ).pack(),
                )
            ]
            for answer, _ in variants
        ]
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
    def profile_actions(
        lang: str = "ru",
        favorite_mode: str | None = None,
        favorite_difficulty: str | None = None,
    ) -> InlineKeyboardMarkup:
        """Profile screen keyboard — Quick start + Training + back.

        Lets the user kick off a session right from the profile without
        bouncing back to the main menu. Quick start row only renders when
        a favorite is configured.
        """
        rows: list[list[InlineKeyboardButton]] = []
        mode_text = mode_label(favorite_mode, lang) if favorite_mode else ""
        if mode_text:
            diff_text = difficulty_label(favorite_difficulty or "medium", lang)
            combined = f"{diff_text} {mode_text}".strip()
            fav_label = get_text("btn_quick_start", lang).format(mode=combined)
            rows.append(
                [
                    InlineKeyboardButton(
                        text=fav_label,
                        callback_data=MenuCB(action="quick_start").pack(),
                    )
                ]
            )
        rows.append(
            [
                InlineKeyboardButton(
                    text=get_text("btn_start_training", lang),
                    callback_data=MenuCB(action="training").pack(),
                ),
                InlineKeyboardButton(
                    text=get_text("btn_back_to_menu", lang),
                    callback_data=BackCB(action="menu").pack(),
                ),
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=rows)

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
