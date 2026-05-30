"""Unit tests for app.utils.ui helpers."""
from __future__ import annotations

import pytest

from app.utils.ui import (
    SEPARATOR,
    format_problem_anchor,
    format_seconds,
    render_progress_bar,
    today_msk,
)


# ---- render_progress_bar --------------------------------------------------


def test_progress_bar_zero_total_returns_empty():
    assert render_progress_bar(0, 0) == ""
    assert render_progress_bar(5, 0) == ""


def test_progress_bar_zero_current_all_empty():
    assert render_progress_bar(0, 10) == "░" * 10


def test_progress_bar_full_when_current_equals_total():
    assert render_progress_bar(10, 10) == "▓" * 10


def test_progress_bar_half():
    bar = render_progress_bar(5, 10)
    assert bar == "▓▓▓▓▓░░░░░"
    assert len(bar) == 10


def test_progress_bar_custom_width():
    bar = render_progress_bar(3, 6, width=12)
    assert len(bar) == 12
    assert bar.count("▓") == 6


def test_progress_bar_overflow_clamped():
    assert render_progress_bar(20, 10) == "▓" * 10


def test_progress_bar_negative_current_clamped():
    assert render_progress_bar(-5, 10) == "░" * 10


def test_progress_bar_rounds_to_nearest():
    # 3 / 10 * 10 = 3 — clean.
    assert render_progress_bar(3, 10).count("▓") == 3
    # 1 / 7 * 10 ≈ 1.43 → rounds to 1.
    assert render_progress_bar(1, 7).count("▓") == 1
    # 4 / 7 * 10 ≈ 5.71 → rounds to 6.
    assert render_progress_bar(4, 7).count("▓") == 6


# ---- format_seconds -------------------------------------------------------


def test_format_seconds_none_returns_empty():
    assert format_seconds(None) == ""


def test_format_seconds_under_ten_uses_one_decimal():
    assert format_seconds(4.234) == "4.2s"
    assert format_seconds(0.05) == "0.1s"


def test_format_seconds_ten_or_more_uses_integer():
    assert format_seconds(12.7) == "13s"
    assert format_seconds(60.0) == "60s"


def test_format_seconds_negative_returns_empty():
    assert format_seconds(-1.0) == ""


# ---- format_problem_anchor ------------------------------------------------


def test_anchor_has_separator_lines(monkeypatch):
    # Stub i18n so the test doesn't depend on real locale wording.
    from app.utils import ui

    monkeypatch.setattr(
        ui, "get_text", lambda k, lang: "🧮 {current} / {total}  {bar}"
    )
    text = format_problem_anchor("47 + 28", current=3, total=10, lang="ru")
    assert SEPARATOR in text
    assert text.count(SEPARATOR) == 2
    assert "47 + 28" in text


def test_anchor_includes_streak_and_time(monkeypatch):
    from app.utils import ui

    monkeypatch.setattr(
        ui, "get_text", lambda k, lang: "{current}/{total} {bar}"
    )
    text = format_problem_anchor(
        "5 * 5", current=2, total=5, lang="ru", streak=3, last_time_s=4.2
    )
    assert "🔥 streak 3" in text
    assert "⏱ 4.2s" in text


def test_anchor_omits_zero_streak(monkeypatch):
    from app.utils import ui

    monkeypatch.setattr(
        ui, "get_text", lambda k, lang: "{current}/{total} {bar}"
    )
    text = format_problem_anchor("1 + 1", current=1, total=5, lang="ru", streak=0)
    assert "🔥" not in text


def test_anchor_includes_feedback_prefix(monkeypatch):
    from app.utils import ui

    monkeypatch.setattr(
        ui, "get_text", lambda k, lang: "{current}/{total} {bar}"
    )
    text = format_problem_anchor(
        "1 + 1", current=2, total=5, lang="ru", feedback_prefix="✅"
    )
    assert text.startswith("✅\n")


# ---- today_msk ------------------------------------------------------------


def test_today_msk_returns_a_date():
    d = today_msk()
    assert hasattr(d, "year") and hasattr(d, "month") and hasattr(d, "day")
