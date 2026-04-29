"""Tests for normal/chi2/fisher/bootstrap inference modules."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import stats

from expkit.inference.bootstrap import bootstrap_ci
from expkit.inference.chi2 import contingency, goodness_of_fit
from expkit.inference.fisher import fisher_exact_2x2
from expkit.inference.normal import (
    one_sample_t,
    one_sample_z,
    two_proportion_z,
    two_sample_t,
)


def test_one_sample_z_at_null_returns_one():
    res = one_sample_z(50, 100, p_null=0.5)
    assert res.point_estimate == pytest.approx(0.5)
    assert res.p_value == pytest.approx(1.0)


def test_two_proportion_z_clear_signal():
    # 600 vs 500 of 1000 is a clearly significant 10pp lift.
    res = two_proportion_z(600, 1000, 500, 1000)
    assert res.statistic > 0
    assert res.p_value < 1e-4
    assert res.point_estimate == pytest.approx(0.1)


def test_two_proportion_z_no_signal_returns_high_pvalue():
    res = two_proportion_z(500, 1000, 510, 1000)
    assert res.p_value > 0.1


def test_two_sample_t_matches_scipy():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, size=100)
    y = rng.normal(0.5, 1, size=100)
    res = two_sample_t(x, y, equal_var=False)
    expected = stats.ttest_ind(x, y, equal_var=False)
    assert res.p_value == pytest.approx(expected.pvalue)


def test_one_sample_t_zero_mean():
    rng = np.random.default_rng(1)
    x = rng.normal(0, 1, size=50)
    res = one_sample_t(x, mu_null=0.0)
    assert 0.0 < res.p_value <= 1.0


def test_chi2_goodness_uniform_pass():
    obs = np.array([10, 12, 9, 11])
    res = goodness_of_fit(obs)
    assert res.dof == 3
    assert res.p_value > 0.5


def test_chi2_goodness_skewed_reject():
    obs = np.array([2, 3, 4, 91])
    res = goodness_of_fit(obs)
    assert res.p_value < 1e-10


def test_chi2_contingency_independent():
    table = np.array([[50, 50], [50, 50]])
    res = contingency(table)
    assert res.p_value == pytest.approx(1.0)


def test_fisher_exact_simple():
    res = fisher_exact_2x2(np.array([[8, 2], [1, 9]]))
    assert res.odds_ratio > 1
    assert res.p_value < 0.05


def test_bootstrap_ci_brackets_truth():
    rng = np.random.default_rng(2)
    data = rng.normal(5.0, 1.0, size=500)
    lo, hi, _ = bootstrap_ci(data, n_boot=1000, alpha=0.05, seed=2)
    assert lo < 5.0 < hi


def test_bootstrap_ci_with_custom_statistic():
    rng = np.random.default_rng(3)
    data = rng.binomial(1, 0.4, size=500)
    lo, hi, draws = bootstrap_ci(data, statistic=np.mean, n_boot=500, seed=3)
    assert 0 <= lo <= hi <= 1
    assert lo < 0.4 < hi
    assert len(draws) == 500
