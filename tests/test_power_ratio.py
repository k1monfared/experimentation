"""Tests for expkit.power.ratio."""

from __future__ import annotations

import numpy as np
import pytest

from expkit.power.ratio import (
    delta_sigma,
    mde,
    required_n,
    simulate_rejection_rate,
    two_arm_z_power,
)


def test_delta_sigma_zero_var_when_d_is_constant():
    # If denominator is constant (sigma_d = 0, cov = 0), the ratio variance
    # collapses to sigma_n^2 / mu_d^2.
    s = delta_sigma(mu_n=2.0, mu_d=4.0, sigma_n=1.0, sigma_d=0.0, cov_nd=0.0)
    assert s == pytest.approx(1.0 / 4.0)


def test_delta_sigma_validation():
    with pytest.raises(ValueError):
        delta_sigma(mu_n=1.0, mu_d=0.0, sigma_n=1.0, sigma_d=1.0)
    with pytest.raises(ValueError):
        delta_sigma(mu_n=1.0, mu_d=1.0, sigma_n=-1.0, sigma_d=1.0)


def test_two_arm_power_at_null_equals_alpha():
    p = two_arm_z_power(diff=0.0, n_per_arm=200, sigma_eff=0.5, alpha=0.05)
    assert p == pytest.approx(0.05, abs=1e-6)


def test_two_arm_power_increases_with_n():
    a = two_arm_z_power(diff=0.05, n_per_arm=50, sigma_eff=0.5)
    b = two_arm_z_power(diff=0.05, n_per_arm=5000, sigma_eff=0.5)
    assert a < b
    assert b > 0.99


def test_required_n_round_trip():
    n = required_n(diff=0.05, sigma_eff=0.5, power=0.8, alpha=0.05)
    p = two_arm_z_power(0.05, n, sigma_eff=0.5)
    assert p >= 0.8
    assert two_arm_z_power(0.05, n - 1, sigma_eff=0.5) < 0.8


def test_required_n_via_moments_matches_via_sigma_eff():
    s = delta_sigma(mu_n=2.0, mu_d=4.0, sigma_n=1.0, sigma_d=0.5, cov_nd=0.1)
    n_direct = required_n(diff=0.05, sigma_eff=s, power=0.8)
    n_indirect = required_n(
        diff=0.05, mu_n=2.0, mu_d=4.0, sigma_n=1.0, sigma_d=0.5, cov_nd=0.1, power=0.8
    )
    assert n_direct == n_indirect


def test_mde_closed_form_matches_power():
    e = mde(n_per_arm=400, sigma_eff=0.5, power=0.8, alpha=0.05, side="greater")
    p = two_arm_z_power(diff=e, n_per_arm=400, sigma_eff=0.5, alpha=0.05, alternative="greater")
    assert p == pytest.approx(0.8, abs=1e-3)


def test_mde_scales_inverse_sqrt_n():
    e_small_n = mde(n_per_arm=100, sigma_eff=0.5)
    e_big_n = mde(n_per_arm=400, sigma_eff=0.5)
    # Quadrupling n should halve the MDE.
    assert e_big_n / e_small_n == pytest.approx(0.5, abs=1e-3)


def test_simulate_matches_closed_form_under_normal_assumption():
    closed = two_arm_z_power(diff=0.1, n_per_arm=200, sigma_eff=0.5)
    rate = simulate_rejection_rate(
        diff=0.1, n_per_arm=200, sigma_eff=0.5, alpha=0.05, n_experiments=2000, seed=0
    )
    assert abs(rate - closed) < 0.03


def test_required_sigma_eff_or_moments():
    with pytest.raises(ValueError):
        required_n(diff=0.05)  # neither sigma_eff nor moments
    with pytest.raises(ValueError):
        two_arm_z_power(diff=0.05, n_per_arm=100)


def test_negative_variance_from_inconsistent_inputs():
    # |cov| > sigma_n * sigma_d should be flagged via negative delta variance.
    with pytest.raises(ValueError):
        delta_sigma(mu_n=10.0, mu_d=1.0, sigma_n=0.1, sigma_d=0.1, cov_nd=10.0)
