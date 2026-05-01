"""Tests for expkit.metrics.quality."""

from __future__ import annotations

import numpy as np
import pytest

from expkit.metrics.quality import predictivity, relative_noise, stability_aa


def test_relative_noise_known_value():
    arr = np.array([10.0, 12.0, 8.0, 11.0, 9.0])
    cv = relative_noise(arr)
    expected = arr.std(ddof=1) / abs(arr.mean())
    assert cv == pytest.approx(expected)


def test_relative_noise_zero_mean_returns_nan():
    arr = np.array([-1.0, 0.0, 1.0])
    assert np.isnan(relative_noise(arr))


def test_stability_aa_well_behaved_distribution():
    rng = np.random.default_rng(0)
    effects = rng.normal(0, 0.05, size=5000)
    s = stability_aa(effects)
    assert abs(s["mean"]) < 0.005
    assert s["std"] == pytest.approx(0.05, abs=0.005)
    assert 0.04 < s["frac_extreme"] < 0.06


def test_predictivity_perfect_correlation():
    x = np.linspace(-1, 1, 50)
    y = 2 * x
    p = predictivity(x, y)
    assert p["pearson_r"] == pytest.approx(1.0)
    assert p["r_squared"] == pytest.approx(1.0)


def test_predictivity_zero_correlation():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 5000)
    y = rng.normal(0, 1, 5000)
    p = predictivity(x, y)
    assert abs(p["pearson_r"]) < 0.05


def test_predictivity_validates_lengths():
    with pytest.raises(ValueError):
        predictivity(np.array([1.0, 2.0]), np.array([1.0]))
