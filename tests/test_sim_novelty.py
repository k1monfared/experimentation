"""Tests for expkit.sim.novelty."""

from __future__ import annotations

import pytest

from expkit.sim.novelty import novelty_event_log


def test_event_log_columns():
    df = novelty_event_log(50, days=10, base_rate=0.1, initial_lift=0.05, half_life_days=5.0, seed=0)
    expected = {"user_id", "arm", "day", "days_since_first_exposure", "exposure_count", "outcome"}
    assert expected.issubset(df.columns)


def test_event_log_arms_present():
    df = novelty_event_log(200, days=5, base_rate=0.1, initial_lift=0.05, half_life_days=5.0, seed=0)
    assert set(df["arm"]) == {"control", "treatment"}


def test_event_log_outcome_binary():
    df = novelty_event_log(100, days=10, base_rate=0.2, initial_lift=0.05, half_life_days=5.0, seed=0)
    assert set(df["outcome"]) <= {0, 1}


def test_event_log_decay_visible_at_high_lift():
    df = novelty_event_log(2000, days=20, base_rate=0.1, initial_lift=0.30, half_life_days=2.0, seed=0)
    treat = df[df["arm"] == "treatment"].dropna(subset=["days_since_first_exposure"])
    early = treat[treat["days_since_first_exposure"] <= 1]["outcome"].mean()
    late = treat[treat["days_since_first_exposure"] >= 8]["outcome"].mean()
    assert early > late


def test_event_log_deterministic():
    a = novelty_event_log(50, days=5, base_rate=0.1, initial_lift=0.05, half_life_days=3.0, seed=7)
    b = novelty_event_log(50, days=5, base_rate=0.1, initial_lift=0.05, half_life_days=3.0, seed=7)
    assert (a["outcome"].values == b["outcome"].values).all()


def test_event_log_no_arrivals_handles_gracefully():
    df = novelty_event_log(20, days=3, base_rate=0.1, initial_lift=0.0, half_life_days=5.0, arrival_rate=0.0, seed=0)
    assert len(df) == 0
