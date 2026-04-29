"""Variance reduction: CUPED."""

from __future__ import annotations

import numpy as np


def cuped(
    y: np.ndarray,
    x: np.ndarray,
    arm: np.ndarray | None = None,
) -> tuple[np.ndarray, float]:
    """CUPED-adjusted outcome.

    ``y`` is the experimental outcome, ``x`` is a pre-experiment covariate
    measured on the same units. ``arm`` (optional) is treatment indicator -- if
    provided, theta is computed pooled. Returns ``(y_adjusted, theta)``.

    The adjusted outcome has expectation equal to that of ``y`` but lower
    variance whenever ``x`` and ``y`` are correlated.
    """
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    cov = np.cov(x, y, ddof=1)
    var_x = cov[0, 0]
    if var_x == 0:
        return y.copy(), 0.0
    theta = cov[0, 1] / var_x
    y_adj = y - theta * (x - x.mean())
    return y_adj, float(theta)


def variance_reduction_ratio(y: np.ndarray, y_adj: np.ndarray) -> float:
    """Fraction of variance removed: 1 - var(y_adj)/var(y)."""
    return float(1 - np.var(y_adj, ddof=1) / np.var(y, ddof=1))
