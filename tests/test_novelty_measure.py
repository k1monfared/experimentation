"""Tests for expkit.novelty.measure."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from expkit.novelty.measure import (
    by_calendar_day,
    by_days_since_exposure,
    by_exposure_count,
)
from expkit.sim.novelty import novelty_event_log


@pytest.fixture
def sample_log():
    return novelty_event_log(500, days=15, base_rate=0.1, initial_lift=0.10, half_life_days=4.0, seed=0)


def test_calendar_day_returns_one_row_per_day(sample_log):
    out = by_calendar_day(sample_log)
    assert "day" in out.columns
    assert {"control", "treatment"}.issubset(out.columns)
    assert (out["day"] == sorted(out["day"])).all()


def test_days_since_exposure_no_negative_values(sample_log):
    out = by_days_since_exposure(sample_log)
    assert (out["days_since_first_exposure"] >= 0).all()
    assert {"treatment", "control"}.issubset(out.columns)


def test_exposure_count_only_treatment(sample_log):
    out = by_exposure_count(sample_log)
    assert "exposure_count" in out.columns
    assert "treatment" in out.columns


def test_calendar_day_handles_minimal_log():
    df = pd.DataFrame({
        "user_id": [0, 1],
        "arm": ["control", "treatment"],
        "day": [0, 0],
        "days_since_first_exposure": [None, 0.0],
        "exposure_count": [0, 1],
        "outcome": [0, 1],
    })
    out = by_calendar_day(df)
    assert len(out) == 1


def test_days_since_decay_high_lift():
    df = novelty_event_log(2000, days=20, base_rate=0.1, initial_lift=0.30, half_life_days=2.0, seed=0)
    out = by_days_since_exposure(df)
    early = out[out["days_since_first_exposure"] <= 1]["treatment"].mean()
    late = out[out["days_since_first_exposure"] >= 8]["treatment"].mean()
    assert early > late
