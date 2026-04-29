"""Bernoulli (coin-toss) sample generators."""

from __future__ import annotations

import numpy as np


def bernoulli_sequence(n: int, p: float = 0.5, seed: int | None = None) -> np.ndarray:
    """Generate ``n`` Bernoulli draws with success probability ``p``.

    Returns a 1-D array of 0s and 1s. The result is deterministic for a given
    ``seed`` so that chapters can recreate the exact sequence.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    rng = np.random.default_rng(seed)
    return rng.binomial(1, p, size=n).astype(np.int8)


def cumulative_heads(seq: np.ndarray) -> np.ndarray:
    """Cumulative count of heads over the toss sequence."""
    return np.cumsum(seq).astype(np.int64)


def running_fraction(seq: np.ndarray) -> np.ndarray:
    """Running fraction of heads after each toss.

    Element ``i`` is ``cumulative_heads(seq)[i] / (i + 1)``.
    """
    n = len(seq)
    if n == 0:
        return np.array([], dtype=float)
    counts = cumulative_heads(seq)
    denom = np.arange(1, n + 1, dtype=float)
    return counts / denom
