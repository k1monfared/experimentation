"""Tests for expkit.inference.multitest."""

from __future__ import annotations

import numpy as np
import pytest

from expkit.inference.multitest import (
    benjamini_hochberg,
    bonferroni,
    holm,
)


def test_bonferroni_simple():
    p = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    res = bonferroni(p, alpha=0.05)
    np.testing.assert_allclose(res.adjusted_p, [0.05, 0.10, 0.15, 0.20, 0.25])
    np.testing.assert_array_equal(res.reject, [True, False, False, False, False])


def test_bonferroni_caps_at_one():
    p = np.array([0.5, 0.6])
    res = bonferroni(p, alpha=0.05)
    np.testing.assert_allclose(res.adjusted_p, [1.0, 1.0])


def test_holm_more_powerful_than_bonferroni():
    # If smallest p clears Bonferroni, Holm rejects the same first p; for
    # later p's Holm uses smaller multipliers so it can reject more.
    p = np.array([0.005, 0.02, 0.04, 0.5])
    bonf = bonferroni(p, alpha=0.05)
    h = holm(p, alpha=0.05)
    # First p rejected by both.
    assert bonf.reject[0] and h.reject[0]
    # Holm should reject at least as many as Bonferroni.
    assert h.reject.sum() >= bonf.reject.sum()


def test_holm_step_down_blocks_later_when_first_fails():
    # If the smallest p does NOT clear m*p<=alpha, no rejection.
    p = np.array([0.03, 0.04, 0.04])  # m=3; smallest adj = 3*0.03=0.09 > 0.05
    h = holm(p, alpha=0.05)
    assert not h.reject.any()


def test_holm_monotonicity():
    # Adjusted p must be non-decreasing along the sorted order of raw p.
    p = np.array([0.001, 0.04, 0.5, 0.8, 0.02])
    h = holm(p)
    order = np.argsort(p)
    sorted_adj = h.adjusted_p[order]
    assert np.all(np.diff(sorted_adj) >= -1e-12)


def test_bh_classical_example():
    # Classic 5-test example: p = [0.001, 0.008, 0.039, 0.041, 0.042], alpha=0.05.
    # Cutoffs: 0.05*1/5=0.01, 0.05*2/5=0.02, 0.05*3/5=0.03, 0.05*4/5=0.04, 0.05*5/5=0.05.
    # Walking from largest: 0.042 vs 0.05 -> reject; step-up rejects all.
    p = np.array([0.001, 0.008, 0.039, 0.041, 0.042])
    res = benjamini_hochberg(p, alpha=0.05)
    np.testing.assert_array_equal(res.reject, [True, True, True, True, True])


def test_bh_rejects_when_smallest_below_threshold_and_others_high():
    # Smallest p clears 1/m * alpha; but high p's prevent step-up from rejecting them.
    # m=4, alpha=0.05. p_(1) <= 0.05/4=0.0125 only if it's tiny.
    p = np.array([0.001, 0.5, 0.6, 0.7])
    res = benjamini_hochberg(p, alpha=0.05)
    np.testing.assert_array_equal(res.reject, [True, False, False, False])


def test_bh_more_powerful_than_holm_in_typical_cases():
    # Five-test scenario where BH catches some that Holm misses.
    p = np.array([0.001, 0.01, 0.025, 0.04, 0.05])
    h = holm(p, alpha=0.05)
    bh = benjamini_hochberg(p, alpha=0.05)
    assert bh.reject.sum() >= h.reject.sum()


def test_bh_monotonicity():
    p = np.array([0.001, 0.04, 0.5, 0.8, 0.02])
    bh = benjamini_hochberg(p)
    order = np.argsort(p)
    sorted_adj = bh.adjusted_p[order]
    assert np.all(np.diff(sorted_adj) >= -1e-12)


def test_validation_rejects_out_of_range_p():
    with pytest.raises(ValueError):
        bonferroni(np.array([0.1, -0.01]))
    with pytest.raises(ValueError):
        holm(np.array([0.1, 1.5]))
    with pytest.raises(ValueError):
        benjamini_hochberg(np.array([0.1, 2.0]))
