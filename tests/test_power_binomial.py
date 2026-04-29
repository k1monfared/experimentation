"""Tests for expkit.power.binomial."""

from __future__ import annotations

import pytest

from expkit.power.binomial import (
    mde,
    normal_approx_power,
    required_n,
    simulate_rejection_rate,
)


def test_power_at_null_equals_alpha_two_sided():
    # Power at p_alt = p_null should equal alpha for two-sided.
    p = normal_approx_power(0.5, 0.5, n=100, alpha=0.05, alternative="two-sided")
    assert p == pytest.approx(0.05, abs=1e-6)


def test_power_increases_with_n():
    p10 = normal_approx_power(0.5, 0.6, n=10)
    p1000 = normal_approx_power(0.5, 0.6, n=1000)
    assert p10 < p1000
    assert p1000 > 0.99


def test_power_increases_with_effect_size():
    a = normal_approx_power(0.5, 0.51, n=200)
    b = normal_approx_power(0.5, 0.6, n=200)
    assert a < b


def test_required_n_round_trip():
    n = required_n(0.5, 0.55, power=0.8, alpha=0.05)
    p = normal_approx_power(0.5, 0.55, n=n)
    assert p >= 0.8
    p_minus = normal_approx_power(0.5, 0.55, n=n - 1)
    assert p_minus < 0.8


def test_mde_greater_side():
    # At n=400 we should be able to detect a moderate one-sided effect.
    e = mde(0.5, n=400, power=0.8, alpha=0.05, side="greater")
    assert 0.01 < e < 0.2


def test_simulate_rejection_rate_at_null():
    # Monte Carlo type I rate should sit near alpha (loose bound for n_exp=300).
    rate = simulate_rejection_rate(0.5, n=200, alpha=0.05, n_experiments=300, seed=0)
    assert 0.0 <= rate <= 0.15
