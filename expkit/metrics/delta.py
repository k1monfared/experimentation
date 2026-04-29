"""Delta method for ratio metrics."""

from __future__ import annotations

import numpy as np


def ratio_mean_and_var(numerator: np.ndarray, denominator: np.ndarray) -> tuple[float, float]:
    """Delta-method estimate of mean and variance of N/D when N and D are paired per unit.

    Returns (point_estimate, variance_of_estimate).
    """
    n = np.asarray(numerator, dtype=float)
    d = np.asarray(denominator, dtype=float)
    if len(n) != len(d):
        raise ValueError("numerator and denominator must be same length")
    n_obs = len(n)
    mean_n = n.mean()
    mean_d = d.mean()
    if mean_d == 0:
        return float("nan"), float("nan")
    point = mean_n / mean_d
    var_n = n.var(ddof=1)
    var_d = d.var(ddof=1)
    cov_nd = np.cov(n, d, ddof=1)[0, 1]
    # Delta method variance of (mean_n / mean_d), divided by N for an estimator of the mean
    var_ratio = (var_n / mean_d ** 2 + (mean_n ** 2) / (mean_d ** 4) * var_d - 2 * mean_n / (mean_d ** 3) * cov_nd) / n_obs
    return float(point), float(var_ratio)


def delta_two_arm(
    n_t: np.ndarray, d_t: np.ndarray, n_c: np.ndarray, d_c: np.ndarray
) -> tuple[float, float, float]:
    """Difference of two ratio metrics with delta-method standard error.

    Returns ``(diff, se, z)`` where ``diff = ratio_t - ratio_c`` and ``z = diff/se``.
    """
    p_t, v_t = ratio_mean_and_var(n_t, d_t)
    p_c, v_c = ratio_mean_and_var(n_c, d_c)
    diff = p_t - p_c
    se = float(np.sqrt(v_t + v_c))
    z = diff / se if se > 0 else float("nan")
    return float(diff), se, float(z)
