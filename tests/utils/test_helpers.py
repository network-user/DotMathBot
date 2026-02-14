"""Tests for app.utils.helpers."""
import pytest
from datetime import datetime, timedelta

from app.utils.helpers import (
    format_time,
    get_streak_status,
    parse_time_from_text,
    get_accuracy_percentage,
    format_stats,
)


class TestFormatTime:
    def test_formats_datetime(self):
        dt = datetime(2025, 2, 14, 15, 30)
        assert format_time(dt) == "14.02.2025 15:30"

    def test_formats_midnight(self):
        dt = datetime(2025, 1, 1, 0, 0)
        assert format_time(dt) == "01.01.2025 00:00"


class TestGetStreakStatus:
    def test_no_last_training_returns_false_and_zero(self):
        is_active, days_diff = get_streak_status(None)
        assert is_active is False
        assert days_diff == 0

    def test_today_training_is_active(self):
        today = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        is_active, days_diff = get_streak_status(today)
        assert is_active is True
        assert days_diff == 0

    def test_yesterday_training_is_active(self):
        yesterday = datetime.now() - timedelta(days=1)
        is_active, days_diff = get_streak_status(yesterday)
        assert is_active is True
        assert days_diff == 1

    def test_two_days_ago_not_active(self):
        two_days = datetime.now() - timedelta(days=2)
        is_active, days_diff = get_streak_status(two_days)
        assert is_active is False
        assert days_diff == 2


class TestParseTimeFromText:
    def test_valid_time(self):
        assert parse_time_from_text("14:30") == {"hours": 14, "minutes": 30}
        assert parse_time_from_text("00:00") == {"hours": 0, "minutes": 0}
        assert parse_time_from_text("23:59") == {"hours": 23, "minutes": 59}

    def test_invalid_format_returns_none(self):
        assert parse_time_from_text("14") is None
        assert parse_time_from_text("14:30:00") is None
        assert parse_time_from_text("") is None
        assert parse_time_from_text("  ") is None

    def test_out_of_range_returns_none(self):
        assert parse_time_from_text("24:00") is None
        assert parse_time_from_text("12:60") is None
        assert parse_time_from_text("-1:30") is None

    def test_non_numeric_returns_none(self):
        assert parse_time_from_text("ab:cd") is None
        assert parse_time_from_text("12:xx") is None

    def test_strips_whitespace(self):
        assert parse_time_from_text("  14:30  ") == {"hours": 14, "minutes": 30}


class TestGetAccuracyPercentage:
    def test_zero_total_returns_zero(self):
        assert get_accuracy_percentage(0, 0) == 0.0
        assert get_accuracy_percentage(5, 0) == 0.0

    def test_all_correct(self):
        assert get_accuracy_percentage(10, 10) == 100.0

    def test_half_correct(self):
        assert get_accuracy_percentage(5, 10) == 50.0

    def test_rounds_to_one_decimal(self):
        assert get_accuracy_percentage(1, 3) == 33.3


class TestFormatStats:
    def test_formats_all_fields(self):
        stats = {
            "correct": 10,
            "incorrect": 2,
            "total": 12,
            "current_streak": 3,
            "max_streak": 5,
        }
        text = format_stats(stats)
        assert "10" in text
        assert "2" in text
        # accuracy 10/12 = 83.3%
        assert "83.3" in text
        assert "3" in text
        assert "5" in text

    def test_missing_keys_use_zero(self):
        text = format_stats({})
        assert "0" in text
