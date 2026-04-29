"""Metric quality diagnostics: noise, stability, predictivity."""

from __future__ import annotations

import numpy as np


def relative_noise(values: np.ndarray) -> float:
    """Coefficient of variation: std / |mean|. Higher = noisier per unit signal."""
    arr = np.asarray(values, dtype=float)
    m = float(np.mean(arr))
    if m == 0:
        return float("nan")
    return float(np.std(arr, ddof=1) / abs(m))


def stability_aa(aa_effects: np.ndarray, alpha: float = 0.05) -> dict:
    """Summary of A/A test effect distribution.

    ``aa_effects`` is the array of measured "treatment - control" values from
    A/A simulations (where the truth is no effect). A well-behaved metric
    should have mean ~0 and a fraction of |effects| > significance threshold
    near alpha.
    """
    arr = np.asarray(aa_effects, dtype=float)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)),
        "frac_extreme": float(np.mean(np.abs(arr) > 1.96 * arr.std(ddof=1))),
    }


def predictivity(short_term: np.ndarray, long_term: np.ndarray) -> dict:
    """Correlation between short-term and long-term per-experiment effects.

    Returns Pearson r and an in-sample R^2 for the linear fit.
    """
    s = np.asarray(short_term, dtype=float)
    l = np.asarray(long_term, dtype=float)
    if len(s) != len(l):
        raise ValueError("short_term and long_term must have the same length")
    cov = np.cov(s, l, ddof=1)
    r = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    return {"pearson_r": float(r), "r_squared": float(r ** 2)}
