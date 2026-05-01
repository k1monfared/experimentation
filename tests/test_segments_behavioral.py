"""Tests for expkit.segments.behavioral."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from expkit.segments.behavioral import (
    BEHAVIORAL_LABELS,
    label_behavioral,
    simulate_population,
)


def test_simulate_population_columns():
    df = simulate_population(500, seed=0)
    expected = {"weekly_active_rate", "contribution_rate", "intentional_rate", "segment"}
    assert expected.issubset(df.columns)


def test_simulate_population_size():
    df = simulate_population(800, seed=0)
    assert len(df) == 800


def test_simulate_population_segments_in_label_set():
    df = simulate_population(500, seed=0)
    assert set(df["segment"]) <= set(BEHAVIORAL_LABELS)


def test_label_behavioral_assigns_all_rows():
    df = simulate_population(300, seed=0)
    labels = label_behavioral(df)
    assert labels.notna().all()
    assert len(labels) == len(df)


def test_label_behavioral_categorizes_predictably():
    # Construct an explicit table with known behavioural axes
    df = pd.DataFrame({
        "weekly_active_rate": [0.9, 0.9, 0.05, 0.05, 0.5, 0.5],
        "contribution_rate": [0.9, 0.05, 0.5, 0.05, 0.5, 0.5],
        "intentional_rate": [0.5, 0.9, 0.9, 0.05, 0.5, 0.5],
    })
    labels = label_behavioral(df)
    # high active + high contrib -> active_contributor
    assert labels.iloc[0] == "active_contributor"
    # high active + low contrib + high intent -> active_consumer
    assert labels.iloc[1] == "active_consumer"
    # low active + high intent -> silent_intentional
    assert labels.iloc[2] == "silent_intentional"
    # low everything -> passive_consumer
    assert labels.iloc[3] == "passive_consumer"


def test_simulate_population_deterministic():
    a = simulate_population(200, seed=42)
    b = simulate_population(200, seed=42)
    pd.testing.assert_frame_equal(a, b)
