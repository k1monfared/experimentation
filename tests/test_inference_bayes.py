"""Tests for expkit.inference.bayes."""

from __future__ import annotations

import numpy as np
import pytest

from expkit.inference.bayes import (
    coin_posterior,
    coin_posterior_conjugate,
    posterior_summary,
)
from expkit.sim.coin import bernoulli_sequence


def test_conjugate_posterior_parameters():
    seq = np.array([1, 1, 0, 1, 0])
    post = coin_posterior_conjugate(seq, prior_alpha=1.0, prior_beta=1.0)
    # 3 heads, 2 tails -> Beta(4, 3)
    assert post.alpha == pytest.approx(4.0)
    assert post.beta == pytest.approx(3.0)
    # mean = 4 / 7
    assert post.mean == pytest.approx(4 / 7)


def test_conjugate_credible_interval_brackets_mean():
    seq = bernoulli_sequence(200, p=0.5, seed=0)
    post = coin_posterior_conjugate(seq)
    lo, hi = post.credible_interval(level=0.95)
    assert lo < post.mean < hi
    assert 0.0 <= lo <= hi <= 1.0


def test_conjugate_prob_greater_than():
    # With Beta(50, 50) the median is 0.5, so P(p > 0.5) ~ 0.5
    seq = np.array([1] * 49 + [0] * 49)
    post = coin_posterior_conjugate(seq)  # Beta(50, 50)
    assert post.prob_greater_than(0.5) == pytest.approx(0.5, abs=0.02)


def test_bayes_factor_strong_evidence_against_null():
    # 90/100 strongly suggests p != 0.5. BF in favor of H1 should be huge.
    from expkit.inference.bayes import bayes_factor_point_vs_uniform

    seq = np.array([1] * 90 + [0] * 10)
    bf = bayes_factor_point_vs_uniform(seq, point=0.5)
    assert bf > 1e10


def test_bayes_factor_weak_data_close_to_one():
    # 5/10 carries minimal information; BF should be O(1).
    from expkit.inference.bayes import bayes_factor_point_vs_uniform

    seq = np.array([1] * 5 + [0] * 5)
    bf = bayes_factor_point_vs_uniform(seq, point=0.5)
    assert 0.1 < bf < 10


def test_posterior_predictive_shape_and_range():
    from expkit.inference.bayes import conjugate_posterior_predictive

    seq = np.array([1] * 60 + [0] * 40)
    preds = conjugate_posterior_predictive(seq, new_n=20, n_samples=500, seed=0)
    assert preds.shape == (500,)
    assert (preds >= 0).all() and (preds <= 20).all()
    # Predictive mean should be close to 0.6 * 20 = 12 (Beta(61, 41) -> mean ~0.598)
    assert 10 < preds.mean() < 14


@pytest.mark.slow
def test_pymc_posterior_matches_conjugate_mean():
    seq = bernoulli_sequence(200, p=0.5, seed=0)
    idata = coin_posterior(seq, seed=123, draws=2000, chains=2, tune=1000, progressbar=False)
    summary = posterior_summary(idata)
    closed_form = coin_posterior_conjugate(seq)
    assert summary["mean"] == pytest.approx(closed_form.mean, abs=0.02)
    lo, hi = closed_form.credible_interval(0.95)
    assert summary["ci_95_low"] == pytest.approx(lo, abs=0.03)
    assert summary["ci_95_high"] == pytest.approx(hi, abs=0.03)
