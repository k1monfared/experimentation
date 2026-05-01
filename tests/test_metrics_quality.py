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


def test_signal_to_noise_with_reference():
    from expkit.metrics.quality import signal_to_noise

    arr = np.array([0.01, 0.0, -0.01, 0.005, -0.005])
    s_only = signal_to_noise(arr)
    s_scaled = signal_to_noise(arr, reference_scale=0.01)
    assert s_only > 0
    assert s_scaled == pytest.approx(s_only / 0.01)


def test_aa_calibration_well_calibrated_pipeline():
    from expkit.metrics.quality import aa_calibration

    rng = np.random.default_rng(0)
    pvals = rng.uniform(0, 1, size=5000)
    res = aa_calibration(pvals, alpha=0.05)
    assert res["n_trials"] == 5000
    assert res["empirical_rate"] == pytest.approx(0.05, abs=0.01)
    assert res["ci_95_low"] < 0.05 < res["ci_95_high"]


def test_aa_calibration_broken_pipeline():
    from expkit.metrics.quality import aa_calibration

    pvals = np.full(500, 0.001)
    res = aa_calibration(pvals, alpha=0.05)
    assert res["empirical_rate"] == 1.0


def test_predictivity_bootstrap_ci_brackets_r():
    rng = np.random.default_rng(0)
    n = 200
    x = rng.normal(0, 1, n)
    y = 0.6 * x + rng.normal(0, 1, n)
    res = predictivity(x, y, n_boot=500, seed=42)
    assert "ci_95_low" in res
    assert res["ci_95_low"] < res["pearson_r"] < res["ci_95_high"]
    assert res["n_boot"] == 500
