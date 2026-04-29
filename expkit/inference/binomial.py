"""Frequentist inference for a single binomial proportion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportion_confint


@dataclass(frozen=True)
class BinomTestResult:
    """Result of a two-sided exact binomial test."""

    successes: int
    n: int
    p_null: float
    p_value: float
    point_estimate: float


def binom_test_exact(
    successes: int,
    n: int,
    p_null: float = 0.5,
    alternative: Literal["two-sided", "less", "greater"] = "two-sided",
) -> BinomTestResult:
    """Exact binomial test against ``p_null``.

    Wraps ``scipy.stats.binomtest``; returned object includes the point estimate.
    """
    if successes < 0 or successes > n:
        raise ValueError("successes must be between 0 and n")
    res = stats.binomtest(successes, n, p=p_null, alternative=alternative)
    return BinomTestResult(
        successes=successes,
        n=n,
        p_null=p_null,
        p_value=float(res.pvalue),
        point_estimate=successes / n if n > 0 else float("nan"),
    )


def wilson_ci(successes: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score confidence interval for a single proportion."""
    lo, hi = proportion_confint(successes, n, alpha=alpha, method="wilson")
    return float(lo), float(hi)


def clopper_pearson_ci(successes: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact Clopper-Pearson confidence interval for a single proportion."""
    lo, hi = proportion_confint(successes, n, alpha=alpha, method="beta")
    return float(lo), float(hi)


def running_wilson_band(seq: np.ndarray, alpha: float = 0.05) -> tuple[np.ndarray, np.ndarray]:
    """Per-toss Wilson CI bounds for the running fraction.

    Returns ``(lower, upper)`` arrays each of length ``len(seq)``.
    """
    cum = np.cumsum(seq).astype(int)
    ns = np.arange(1, len(seq) + 1)
    lows = np.empty_like(ns, dtype=float)
    highs = np.empty_like(ns, dtype=float)
    for i, (k, n) in enumerate(zip(cum, ns)):
        lo, hi = wilson_ci(int(k), int(n), alpha=alpha)
        lows[i] = lo
        highs[i] = hi
    return lows, highs
