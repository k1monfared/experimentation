"""Tests for expkit.sim.die."""

from __future__ import annotations

import numpy as np
import pytest

from expkit.sim.die import (
    dirichlet_posterior_mean,
    face_counts,
    fair_die_rolls,
    loaded_die_rolls,
)


def test_fair_die_rolls_shape_and_range():
    rolls = fair_die_rolls(500, sides=6, seed=0)
    assert rolls.shape == (500,)
    assert rolls.min() >= 1
    assert rolls.max() <= 6


def test_fair_die_rolls_deterministic():
    a = fair_die_rolls(200, seed=42)
    b = fair_die_rolls(200, seed=42)
    np.testing.assert_array_equal(a, b)


def test_fair_die_supports_other_sides():
    rolls = fair_die_rolls(100, sides=20, seed=0)
    assert rolls.max() <= 20
    assert rolls.min() >= 1


def test_loaded_die_respects_probabilities():
    p = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
    rolls = loaded_die_rolls(50, p=p, seed=0)
    assert (rolls == 6).all()


def test_loaded_die_validates_probabilities():
    with pytest.raises(ValueError):
        loaded_die_rolls(10, p=np.array([0.5, 0.5, 0.5]))


def test_face_counts_shape():
    rolls = fair_die_rolls(60, seed=0)
    counts = face_counts(rolls)
    assert counts.shape == (6,)
    assert counts.sum() == 60


def test_face_counts_supports_extra_sides():
    rolls = fair_die_rolls(20, sides=8, seed=0)
    counts = face_counts(rolls, sides=8)
    assert counts.shape == (8,)
    assert counts.sum() == 20


def test_dirichlet_posterior_mean_uniform_prior():
    counts = np.array([10, 10, 10, 10, 10, 10])
    mean = dirichlet_posterior_mean(counts)
    np.testing.assert_allclose(mean, np.full(6, 1 / 6))


def test_dirichlet_posterior_mean_with_loaded():
    counts = np.array([5, 5, 5, 5, 5, 75])
    mean = dirichlet_posterior_mean(counts)
    assert mean.sum() == pytest.approx(1.0)
    assert mean[5] > 0.6


def test_dirichlet_posterior_mean_custom_prior():
    counts = np.zeros(6, dtype=int)
    prior = np.array([2.0, 2.0, 2.0, 2.0, 2.0, 100.0])
    mean = dirichlet_posterior_mean(counts, prior=prior)
    assert mean[5] > 0.85
