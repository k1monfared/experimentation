"""Multiple-testing corrections: Bonferroni, Holm, Benjamini-Hochberg.

These take an array of raw p-values and return adjusted p-values along with a
boolean reject vector at level ``alpha``.

- ``bonferroni``: controls the family-wise error rate (FWER); strict, loses
  power as the family grows.
- ``holm``: also controls FWER; uniformly more powerful than Bonferroni.
- ``benjamini_hochberg``: controls the false discovery rate (FDR) under
  independence (and certain forms of positive dependence). Much more powerful
  than FWER methods when the family is large.

All return adjusted p-values capped at 1.0; the reject decision is
``adjusted_p <= alpha``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MultiTestResult:
    raw_p: np.ndarray
    adjusted_p: np.ndarray
    reject: np.ndarray
    method: str
    alpha: float


def bonferroni(p_values: np.ndarray, alpha: float = 0.05) -> MultiTestResult:
    """Bonferroni: adjusted_p = min(m * p, 1). FWER controlled at alpha."""
    p = np.asarray(p_values, dtype=float)
    if np.any((p < 0) | (p > 1)):
        raise ValueError("p_values must lie in [0, 1]")
    m = p.size
    adj = np.minimum(p * m, 1.0)
    return MultiTestResult(raw_p=p, adjusted_p=adj, reject=adj <= alpha, method="bonferroni", alpha=alpha)


def holm(p_values: np.ndarray, alpha: float = 0.05) -> MultiTestResult:
    """Holm step-down: sort p ascending; reject p_(i) if p_(j) <= alpha/(m-j+1)
    for all j <= i. The adjusted p is the running max of (m - rank + 1) * p_(i).
    """
    p = np.asarray(p_values, dtype=float)
    if np.any((p < 0) | (p > 1)):
        raise ValueError("p_values must lie in [0, 1]")
    m = p.size
    order = np.argsort(p)
    sorted_p = p[order]
    # Multipliers for sorted p: smallest p gets m, next m-1, ..., largest gets 1.
    multipliers = np.arange(m, 0, -1)
    raw_adj = sorted_p * multipliers
    # Step-down monotonicity: enforce non-decreasing as we walk down sorted order.
    np.maximum.accumulate(raw_adj, out=raw_adj)
    raw_adj = np.minimum(raw_adj, 1.0)
    # Map back to original order.
    adj = np.empty_like(raw_adj)
    adj[order] = raw_adj
    return MultiTestResult(raw_p=p, adjusted_p=adj, reject=adj <= alpha, method="holm", alpha=alpha)


def benjamini_hochberg(p_values: np.ndarray, alpha: float = 0.05) -> MultiTestResult:
    """Benjamini-Hochberg step-up FDR control.

    Sort p ascending. Reject p_(i) iff p_(i) <= (i/m) * alpha for some i; the
    largest such i fixes the cutoff and everything ranked at or below i is
    rejected. Adjusted p (q-values) are the running min from the right of
    ``p_(i) * m / i``, capped at 1.
    """
    p = np.asarray(p_values, dtype=float)
    if np.any((p < 0) | (p > 1)):
        raise ValueError("p_values must lie in [0, 1]")
    m = p.size
    order = np.argsort(p)
    sorted_p = p[order]
    ranks = np.arange(1, m + 1)
    raw_adj = sorted_p * m / ranks
    # Step-up: enforce non-increasing as we walk from largest p back to smallest.
    raw_adj = np.minimum.accumulate(raw_adj[::-1])[::-1]
    raw_adj = np.minimum(raw_adj, 1.0)
    adj = np.empty_like(raw_adj)
    adj[order] = raw_adj
    return MultiTestResult(raw_p=p, adjusted_p=adj, reject=adj <= alpha, method="benjamini_hochberg", alpha=alpha)
