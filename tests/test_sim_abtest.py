"""Tests for expkit.sim.abtest."""

from __future__ import annotations

import numpy as np
import pytest

from expkit.sim.abtest import (
    stratified_binary,
    two_arm_binary,
    two_arm_continuous,
)


def test_two_arm_binary_shape_and_range():
    exp = two_arm_binary(500, p_control=0.1, p_treatment=0.2, seed=0)
    assert exp.control.shape == (500,)
    assert exp.treatment.shape == (500,)
    assert set(np.unique(exp.control).tolist()).issubset({0, 1})
    assert set(np.unique(exp.treatment).tolist()).issubset({0, 1})


def test_two_arm_binary_means_match_truth():
    exp = two_arm_binary(20000, p_control=0.10, p_treatment=0.13, seed=0)
    assert exp.control.mean() == pytest.approx(0.10, abs=0.02)
    assert exp.treatment.mean() == pytest.approx(0.13, abs=0.02)


def test_two_arm_binary_deterministic():
    a = two_arm_binary(100, 0.3, 0.5, seed=7)
    b = two_arm_binary(100, 0.3, 0.5, seed=7)
    np.testing.assert_array_equal(a.control, b.control)
    np.testing.assert_array_equal(a.treatment, b.treatment)


def test_two_arm_continuous_means_match():
    exp = two_arm_continuous(2000, mu_control=10.0, mu_treatment=10.5, sigma=2.0, seed=0)
    assert exp.control.mean() == pytest.approx(10.0, abs=0.2)
    assert exp.treatment.mean() == pytest.approx(10.5, abs=0.2)


def test_stratified_binary_returns_per_stratum():
    # stratified_binary delegates to two_arm_binary with n_per_arm = stratum size,
    # so each stratum gets `n` controls + `n` treatments.
    strata = stratified_binary(
        strata_sizes={"a": 100, "b": 200},
        p_by_stratum={"a": (0.10, 0.20), "b": (0.05, 0.07)},
        seed=0,
    )
    assert set(strata.keys()) == {"a", "b"}
    assert len(strata["a"].control) == 100
    assert len(strata["a"].treatment) == 100
    assert len(strata["b"].control) == 200
    assert len(strata["b"].treatment) == 200


def test_stratified_binary_validates_keys():
    with pytest.raises(ValueError):
        stratified_binary(
            strata_sizes={"a": 50},
            p_by_stratum={"b": (0.1, 0.2)},
            seed=0,
        )
