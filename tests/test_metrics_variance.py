"""Tests for expkit.metrics.variance (CUPED)."""

from __future__ import annotations

import numpy as np
import pytest

from expkit.metrics.variance import cuped, variance_reduction_ratio


def test_cuped_reduces_variance_when_correlated():
    rng = np.random.default_rng(0)
    n = 4000
    x = rng.normal(0, 1, n)
    y = 0.8 * x + rng.normal(0, 0.5, n)
    y_adj, theta = cuped(y, x)
    assert theta == pytest.approx(0.8, abs=0.05)
    assert y_adj.var() < y.var()
    reduction = variance_reduction_ratio(y, y_adj)
    assert reduction > 0.5


def test_cuped_zero_correlation_no_change():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 2000)
    y = rng.normal(0, 1, 2000)
    _, theta = cuped(y, x)
    assert abs(theta) < 0.05


def test_cuped_preserves_mean():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 2000)
    y = 0.5 * x + 5 + rng.normal(0, 1, 2000)
    y_adj, _ = cuped(y, x)
    assert y_adj.mean() == pytest.approx(y.mean(), abs=0.01)


def test_cuped_handles_constant_x():
    y = np.array([1.0, 2.0, 3.0])
    x = np.array([5.0, 5.0, 5.0])
    y_adj, theta = cuped(y, x)
    assert theta == 0.0
    np.testing.assert_array_equal(y_adj, y)


def test_variance_reduction_ratio_zero_for_no_change():
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    assert variance_reduction_ratio(arr, arr) == pytest.approx(0.0)
