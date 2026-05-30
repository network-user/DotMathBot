"""Tests for the Daily Challenge generator (seed determinism + spec shape)."""
from __future__ import annotations

from datetime import date

import pytest

from app.handlers.daily import DAILY_PROBLEM_COUNT, daily_seed, generate_daily_specs


def test_daily_seed_is_deterministic():
    d = date(2026, 1, 15)
    assert daily_seed(d) == daily_seed(d)


def test_daily_seed_differs_for_adjacent_days():
    s1 = daily_seed(date(2026, 1, 15))
    s2 = daily_seed(date(2026, 1, 16))
    assert s1 != s2


def test_generate_daily_specs_count():
    specs = generate_daily_specs(daily_seed(date(2026, 1, 15)))
    assert len(specs) == DAILY_PROBLEM_COUNT


def test_generate_daily_specs_deterministic():
    seed = daily_seed(date(2026, 2, 1))
    s1 = generate_daily_specs(seed)
    s2 = generate_daily_specs(seed)
    assert s1 == s2


def test_generate_daily_specs_shape():
    specs = generate_daily_specs(daily_seed(date(2026, 3, 1)))
    for spec in specs:
        assert set(spec.keys()) >= {
            "first_num",
            "second_num",
            "operation",
            "answer",
            "formatted_text",
            "metadata",
        }
        assert isinstance(spec["answer"], int)
