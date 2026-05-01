"""Tests for expkit.sim.user_segments."""

from __future__ import annotations

import pytest

from expkit.sim.user_segments import (
    SegmentSpec,
    imbalanced_assignment,
    segmented_binary,
)


SPECS = [
    SegmentSpec("low", 0.6, 0.10, 0.05),
    SegmentSpec("high", 0.4, 0.40, 0.05),
]


def test_segmented_binary_returns_each_segment():
    pop = segmented_binary(2000, SPECS, seed=0)
    assert set(pop.keys()) == {"low", "high"}
    for spec in SPECS:
        sub = pop[spec.name]
        n = len(sub["control"]) + len(sub["treatment"])
        assert n == int(round(2000 * spec.fraction))


def test_segmented_binary_means_track_truth():
    pop = segmented_binary(20000, SPECS, seed=0)
    for spec in SPECS:
        c = pop[spec.name]["control"].mean()
        t = pop[spec.name]["treatment"].mean()
        assert c == pytest.approx(spec.baseline, abs=0.02)
        assert t == pytest.approx(spec.baseline + spec.treatment_lift, abs=0.02)


def test_segmented_binary_validates_fractions():
    bad = [SegmentSpec("x", 0.5, 0.1, 0.0), SegmentSpec("y", 0.4, 0.1, 0.0)]
    with pytest.raises(ValueError):
        segmented_binary(100, bad)


def test_imbalanced_assignment_respects_share():
    shares = {"low": 0.2, "high": 0.8}
    pop = imbalanced_assignment(20000, SPECS, shares, seed=0)
    low_treat_frac = len(pop["low"]["treatment"]) / (len(pop["low"]["control"]) + len(pop["low"]["treatment"]))
    high_treat_frac = len(pop["high"]["treatment"]) / (len(pop["high"]["control"]) + len(pop["high"]["treatment"]))
    assert low_treat_frac == pytest.approx(0.2, abs=0.01)
    assert high_treat_frac == pytest.approx(0.8, abs=0.01)


def test_segmented_binary_deterministic():
    a = segmented_binary(500, SPECS, seed=42)
    b = segmented_binary(500, SPECS, seed=42)
    for k in a:
        assert (a[k]["control"] == b[k]["control"]).all()
        assert (a[k]["treatment"] == b[k]["treatment"]).all()
