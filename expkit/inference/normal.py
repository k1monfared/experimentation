"""Normal-approximation tests: one- and two-sample z and t."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class TestResult:
    statistic: float
    p_value: float
    point_estimate: float


def one_sample_z(successes: int, n: int, p_null: float = 0.5, alternative: str = "two-sided") -> TestResult:
    """Wald-style one-sample z-test for a proportion."""
    p_hat = successes / n
    se = np.sqrt(p_null * (1 - p_null) / n)
    z = (p_hat - p_null) / se
    if alternative == "two-sided":
        pval = 2 * stats.norm.sf(abs(z))
    elif alternative == "greater":
        pval = stats.norm.sf(z)
    elif alternative == "less":
        pval = stats.norm.cdf(z)
    else:
        raise ValueError(f"unknown alternative: {alternative}")
    return TestResult(statistic=float(z), p_value=float(pval), point_estimate=float(p_hat))


def two_proportion_z(s1: int, n1: int, s2: int, n2: int, alternative: str = "two-sided") -> TestResult:
    """Two-sample z-test on a difference of proportions (pooled SE)."""
    p1, p2 = s1 / n1, s2 / n2
    p_pool = (s1 + s2) / (n1 + n2)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return TestResult(statistic=float("nan"), p_value=1.0, point_estimate=float(p1 - p2))
    z = (p1 - p2) / se
    if alternative == "two-sided":
        pval = 2 * stats.norm.sf(abs(z))
    elif alternative == "greater":
        pval = stats.norm.sf(z)
    elif alternative == "less":
        pval = stats.norm.cdf(z)
    else:
        raise ValueError(f"unknown alternative: {alternative}")
    return TestResult(statistic=float(z), p_value=float(pval), point_estimate=float(p1 - p2))


def two_sample_t(x: np.ndarray, y: np.ndarray, equal_var: bool = False) -> TestResult:
    """Welch's two-sample t-test (default) or Student t with pooled variance."""
    res = stats.ttest_ind(x, y, equal_var=equal_var)
    return TestResult(statistic=float(res.statistic), p_value=float(res.pvalue), point_estimate=float(np.mean(x) - np.mean(y)))


def one_sample_t(x: np.ndarray, mu_null: float = 0.0) -> TestResult:
    """One-sample t-test against ``mu_null``."""
    res = stats.ttest_1samp(x, popmean=mu_null)
    return TestResult(statistic=float(res.statistic), p_value=float(res.pvalue), point_estimate=float(np.mean(x)))
