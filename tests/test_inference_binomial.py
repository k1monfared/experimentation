"""Tests for expkit.inference.binomial."""

from __future__ import annotations

import pytest
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

from expkit.inference.binomial import (
    binom_test_exact,
    clopper_pearson_ci,
    running_wilson_band,
    wilson_ci,
)
from expkit.sim.coin import bernoulli_sequence


def test_binom_test_matches_scipy():
    res = binom_test_exact(60, 100, p_null=0.5)
    expected = stats.binomtest(60, 100, p=0.5).pvalue
    assert res.p_value == pytest.approx(expected)
    assert res.point_estimate == pytest.approx(0.6)


def test_binom_test_one_sided_greater():
    res = binom_test_exact(60, 100, p_null=0.5, alternative="greater")
    expected = stats.binomtest(60, 100, p=0.5, alternative="greater").pvalue
    assert res.p_value == pytest.approx(expected)


def test_wilson_ci_matches_statsmodels():
    lo, hi = wilson_ci(60, 100)
    sm_lo, sm_hi = proportion_confint(60, 100, alpha=0.05, method="wilson")
    assert lo == pytest.approx(sm_lo)
    assert hi == pytest.approx(sm_hi)


def test_clopper_pearson_ci_matches_statsmodels():
    lo, hi = clopper_pearson_ci(60, 100)
    sm_lo, sm_hi = proportion_confint(60, 100, alpha=0.05, method="beta")
    assert lo == pytest.approx(sm_lo)
    assert hi == pytest.approx(sm_hi)


def test_running_band_shape_and_bounds():
    seq = bernoulli_sequence(50, p=0.5, seed=7)
    lows, highs = running_wilson_band(seq, alpha=0.05)
    assert lows.shape == (50,)
    assert highs.shape == (50,)
    assert (lows <= highs).all()
    assert (lows >= 0).all() and (highs <= 1).all()


def test_invalid_successes_raises():
    with pytest.raises(ValueError):
        binom_test_exact(101, 100)
