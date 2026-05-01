"""Tests for expkit.power.continuous."""

from __future__ import annotations

import numpy as np
import pytest

from expkit.power.continuous import (
    mde,
    required_n,
    simulate_rejection_rate,
    two_sample_z_power,
)


def test_power_at_null_equals_alpha_two_sided():
    p = two_sample_z_power(mu_c=0.0, mu_t=0.0, sigma=1.0, n_per_arm=200, alpha=0.05)
    assert p == pytest.approx(0.05, abs=1e-6)


def test_power_increases_with_n():
    p_small = two_sample_z_power(0.0, 0.2, sigma=1.0, n_per_arm=20)
    p_large = two_sample_z_power(0.0, 0.2, sigma=1.0, n_per_arm=2000)
    assert p_small < p_large
    assert p_large > 0.99


def test_power_increases_with_effect_size():
    a = two_sample_z_power(0.0, 0.05, sigma=1.0, n_per_arm=200)
    b = two_sample_z_power(0.0, 0.30, sigma=1.0, n_per_arm=200)
    assert a < b


def test_required_n_round_trip():
    n = required_n(0.0, 0.2, sigma=1.0, power=0.8, alpha=0.05)
    p = two_sample_z_power(0.0, 0.2, sigma=1.0, n_per_arm=n)
    assert p >= 0.8
    p_minus = two_sample_z_power(0.0, 0.2, sigma=1.0, n_per_arm=n - 1)
    assert p_minus < 0.8


def test_mde_closed_form_matches_inversion():
    # MDE at n_per_arm=400, power=0.8, alpha=0.05, one-sided.
    e = mde(sigma=1.0, n_per_arm=400, power=0.8, alpha=0.05, side="greater")
    p = two_sample_z_power(0.0, e, sigma=1.0, n_per_arm=400, alpha=0.05, alternative="greater")
    assert p == pytest.approx(0.8, abs=1e-3)


def test_required_n_scales_with_inverse_square_effect():
    # For two-sample z, n ~ (z_a + z_b)^2 * 2 * sigma^2 / delta^2; halving the
    # effect should roughly quadruple n.
    n_big = required_n(0.0, 0.2, sigma=1.0)
    n_small = required_n(0.0, 0.1, sigma=1.0)
    ratio = n_small / n_big
    assert 3.6 < ratio < 4.4


def test_simulate_rejection_rate_at_null_near_alpha():
    rate = simulate_rejection_rate(
        mu_c=0.0, mu_t=0.0, sigma=1.0, n_per_arm=200, alpha=0.05, n_experiments=400, seed=0
    )
    # Welch t-test type-I rate with n=200 should be near 5% for normal data.
    assert 0.0 <= rate <= 0.12


def test_simulate_rejection_rate_under_alt_close_to_closed_form():
    # Picking a moderate effect; Monte Carlo should be in the ballpark of the
    # closed form (Welch t and z agree closely at this n).
    closed = two_sample_z_power(0.0, 0.3, sigma=1.0, n_per_arm=200)
    rate = simulate_rejection_rate(
        mu_c=0.0, mu_t=0.3, sigma=1.0, n_per_arm=200, alpha=0.05, n_experiments=600, seed=1
    )
    assert abs(rate - closed) < 0.06


def test_validation_errors():
    with pytest.raises(ValueError):
        two_sample_z_power(0.0, 0.1, sigma=0.0, n_per_arm=100)
    with pytest.raises(ValueError):
        two_sample_z_power(0.0, 0.1, sigma=1.0, n_per_arm=1)
    with pytest.raises(ValueError):
        two_sample_z_power(0.0, 0.1, sigma=1.0, n_per_arm=100, alternative="bogus")
    with pytest.raises(ValueError):
        mde(sigma=1.0, n_per_arm=100, power=0.0)
