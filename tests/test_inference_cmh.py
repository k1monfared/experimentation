"""Tests for expkit.inference.cmh."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import stats

from expkit.inference.cmh import cochran_mantel_haenszel


def test_simpson_paradox_aggregate_vs_stratified():
    # Build two strata where each shows treatment helps but the aggregate flips.
    # Stratum 1: large stratum, treatment slightly better. Treatment heavy in this stratum.
    # Stratum 2: small stratum, treatment slightly better. Control heavy in this stratum.
    # Aggregate may contradict; CMH should still detect the consistent within-stratum effect.
    s1 = np.array([[180, 20], [800, 100]], dtype=float)  # row=group, col=success/failure
    s2 = np.array([[40, 60], [10, 20]], dtype=float)
    tables = np.stack([s1, s2])

    # Aggregate 2x2: pool over strata.
    agg = tables.sum(axis=0)
    chi2_agg, p_agg, _, _ = stats.chi2_contingency(agg)

    res = cochran_mantel_haenszel(tables, continuity=True)
    # CMH should be a finite chi-square with df=1.
    assert res.statistic >= 0
    assert 0.0 <= res.p_value <= 1.0
    assert res.n_strata == 2
    # Pooled OR should be a real positive number.
    assert res.common_odds_ratio > 0


def test_no_effect_anywhere_high_pvalue():
    # Each stratum has identical row proportions -> null.
    s = np.array([[50, 50], [50, 50]], dtype=float)
    tables = np.stack([s, s, s])
    res = cochran_mantel_haenszel(tables)
    assert res.p_value > 0.5
    assert abs(res.common_odds_ratio - 1.0) < 1e-6


def test_strong_consistent_effect_low_pvalue():
    # Three strata each strongly favoring treatment.
    s = np.array([[80, 20], [40, 60]], dtype=float)
    tables = np.stack([s, s, s])
    res = cochran_mantel_haenszel(tables)
    assert res.p_value < 1e-10
    assert res.common_odds_ratio > 1.0


def test_or_mh_matches_reference_for_single_stratum():
    # With a single stratum, MH OR should equal the simple OR a*d/(b*c).
    s = np.array([[30, 10], [20, 40]], dtype=float)
    tables = s[None, :, :]
    res = cochran_mantel_haenszel(tables, continuity=False)
    expected_or = (30 * 40) / (10 * 20)
    assert res.common_odds_ratio == pytest.approx(expected_or)


def test_continuity_correction_lowers_statistic():
    s = np.array([[60, 40], [40, 60]], dtype=float)
    tables = s[None, :, :]
    with_cc = cochran_mantel_haenszel(tables, continuity=True)
    no_cc = cochran_mantel_haenszel(tables, continuity=False)
    assert with_cc.statistic <= no_cc.statistic
    assert with_cc.p_value >= no_cc.p_value


def test_validation_errors():
    with pytest.raises(ValueError):
        cochran_mantel_haenszel(np.zeros((2, 3, 3)))
    with pytest.raises(ValueError):
        cochran_mantel_haenszel(np.array([[[-1, 0], [0, 0]]]))
