"""Multinomial (six-sided die) sample generators."""

from __future__ import annotations

import numpy as np


def fair_die_rolls(n: int, sides: int = 6, seed: int | None = None) -> np.ndarray:
    """Generate ``n`` rolls of a fair ``sides``-sided die.

    Returns a 1-D array of integers in ``[1, sides]``.
    """
    rng = np.random.default_rng(seed)
    return rng.integers(1, sides + 1, size=n)


def loaded_die_rolls(n: int, p: np.ndarray, seed: int | None = None) -> np.ndarray:
    """Generate ``n`` rolls of a die with face probabilities ``p``.

    ``p`` is a 1-D array summing to 1; faces are labelled 1 through len(p).
    """
    p = np.asarray(p, dtype=float)
    if not np.isclose(p.sum(), 1.0):
        raise ValueError("p must sum to 1")
    rng = np.random.default_rng(seed)
    sides = len(p)
    return rng.choice(np.arange(1, sides + 1), size=n, p=p)


def face_counts(rolls: np.ndarray, sides: int = 6) -> np.ndarray:
    """Count occurrences of each face. Returns an array of length ``sides``."""
    return np.bincount(rolls.astype(int), minlength=sides + 1)[1:]


def dirichlet_posterior_mean(counts: np.ndarray, prior: np.ndarray | None = None) -> np.ndarray:
    """Closed-form Dirichlet posterior mean for face probabilities.

    With a Dirichlet(prior) prior and observed ``counts``, posterior is
    Dirichlet(prior + counts) and its mean is component-wise normalized.
    """
    counts = np.asarray(counts, dtype=float)
    if prior is None:
        prior = np.ones_like(counts)
    posterior_alpha = prior + counts
    return posterior_alpha / posterior_alpha.sum()
