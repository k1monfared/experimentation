"""Tests for expkit.sim.coin."""

from __future__ import annotations

import numpy as np
import pytest

from expkit.sim.coin import bernoulli_sequence, cumulative_heads, running_fraction


def test_sequence_length():
    seq = bernoulli_sequence(50, p=0.3, seed=0)
    assert seq.shape == (50,)
    assert set(np.unique(seq).tolist()).issubset({0, 1})


def test_sequence_is_deterministic_for_fixed_seed():
    a = bernoulli_sequence(200, p=0.4, seed=42)
    b = bernoulli_sequence(200, p=0.4, seed=42)
    np.testing.assert_array_equal(a, b)


def test_different_seeds_give_different_sequences():
    a = bernoulli_sequence(200, p=0.5, seed=1)
    b = bernoulli_sequence(200, p=0.5, seed=2)
    assert not np.array_equal(a, b)


def test_cumulative_heads_matches_cumsum():
    seq = bernoulli_sequence(100, p=0.6, seed=0)
    np.testing.assert_array_equal(cumulative_heads(seq), np.cumsum(seq))


def test_running_fraction_endpoint_matches_mean():
    seq = bernoulli_sequence(500, p=0.5, seed=0)
    rf = running_fraction(seq)
    assert rf[-1] == pytest.approx(seq.mean())


def test_running_fraction_handles_empty():
    rf = running_fraction(np.array([], dtype=int))
    assert rf.size == 0


def test_invalid_p_raises():
    with pytest.raises(ValueError):
        bernoulli_sequence(10, p=1.5)


def test_invalid_n_raises():
    with pytest.raises(ValueError):
        bernoulli_sequence(-1, p=0.5)
