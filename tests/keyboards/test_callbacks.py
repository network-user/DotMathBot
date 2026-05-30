"""Round-trip tests for CallbackData factories.

Each factory must pack→unpack losslessly and have a unique prefix.
"""
from __future__ import annotations

import pytest

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


@pytest.mark.parametrize(
    "factory,kwargs",
    [
        (MenuCB, {"action": "training"}),
        (BackCB, {"action": "menu"}),
        (TrainingCB, {"action": "difficulty", "difficulty": "hard"}),
        (TrainingCB, {"action": "mode", "mode": "choose"}),
        (TrainingCB, {"action": "answer", "idx": 3, "answer": 42}),
        (TrainingCB, {"action": "skip"}),
        (TrainingCB, {"action": "exit"}),
        (TrainingCB, {"action": "retry_mistakes", "session_kind": "retry"}),
        (ProfileCB, {"action": "toggle_top"}),
        (LeaderboardCB, {"action": "page", "mode": "daily", "page": 20}),
        (NotifCB, {"action": "select", "preset": "morning"}),
        (NotifCB, {"action": "cancel_custom"}),
        (AdminCB, {"action": "users", "page": 30}),
        (TipsCB, {"action": "multiplication"}),
    ],
)
def test_roundtrip(factory, kwargs):
    packed = factory(**kwargs).pack()
    unpacked = factory.unpack(packed)
    for k, v in kwargs.items():
        assert getattr(unpacked, k) == v


def test_prefixes_are_distinct():
    factories = [MenuCB, BackCB, TrainingCB, ProfileCB, LeaderboardCB, NotifCB, AdminCB, TipsCB]
    prefixes = {f.__prefix__ for f in factories}
    assert len(prefixes) == len(factories)


def test_training_action_set_includes_new_actions():
    # Smoke: make sure none of the new actions accidentally clash with
    # an existing prefix when packed.
    for action in ("difficulty", "mode", "answer", "skip", "exit", "retry_mistakes", "daily_start"):
        TrainingCB.unpack(TrainingCB(action=action).pack())
