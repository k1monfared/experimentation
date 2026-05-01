"""Tests for expkit.metrics.delta (delta method for ratio metrics)."""

from __future__ import annotations

import numpy as np
import pytest

from expkit.metrics.delta import delta_two_arm, ratio_mean_and_var


def test_ratio_point_estimate():
    n = np.array([10.0, 20.0, 30.0])
    d = np.array([2.0, 4.0, 6.0])
    point, var = ratio_mean_and_var(n, d)
    assert point == pytest.approx(60.0 / 12.0)


def test_ratio_validates_lengths():
    with pytest.raises(ValueError):
        ratio_mean_and_var(np.array([1.0]), np.array([1.0, 2.0]))


def test_ratio_handles_zero_denominator():
    n = np.array([1.0, 2.0])
    d = np.array([0.0, 0.0])
    point, var = ratio_mean_and_var(n, d)
    assert np.isnan(point)
    assert np.isnan(var)


def test_delta_two_arm_zero_effect():
    rng = np.random.default_rng(0)
    n_t = rng.normal(2.0, 0.5, 2000)
    d_t = rng.uniform(1.0, 3.0, 2000)
    n_c = rng.normal(2.0, 0.5, 2000)
    d_c = rng.uniform(1.0, 3.0, 2000)
    diff, se, z = delta_two_arm(n_t, d_t, n_c, d_c)
    assert abs(z) < 4.0
    assert se > 0


def test_delta_two_arm_clear_signal():
    rng = np.random.default_rng(0)
    # Treatment ratio is meaningfully larger
    sess_c = rng.poisson(8, 3000)
    rev_c = rng.normal(2.0 * sess_c, 4)
    sess_t = rng.poisson(8, 3000)
    rev_t = rng.normal(2.5 * sess_t, 4)
    diff, se, z = delta_two_arm(rev_t, sess_t, rev_c, sess_c)
    assert diff > 0.3
    assert z > 5.0


def test_delta_two_arm_symmetric():
    rng = np.random.default_rng(0)
    n_t = rng.normal(2, 0.5, 1500)
    d_t = rng.uniform(1, 3, 1500)
    n_c = rng.normal(2, 0.5, 1500)
    d_c = rng.uniform(1, 3, 1500)
    diff_tc, _, _ = delta_two_arm(n_t, d_t, n_c, d_c)
    diff_ct, _, _ = delta_two_arm(n_c, d_c, n_t, d_t)
    assert diff_tc == pytest.approx(-diff_ct, abs=1e-9)
