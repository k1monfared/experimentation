"""Power, sample size, and minimum detectable effect for continuous outcomes.

Two-sample setting: control mean ``mu_c``, treatment mean ``mu_t``, common
standard deviation ``sigma`` (assumed equal across arms; pass an effective
sigma if the arms differ). All formulas use the standard two-sample z
approximation, which becomes the t-test for moderate-to-large N.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def two_sample_z_power(
    mu_c: float,
    mu_t: float,
    sigma: float,
    n_per_arm: int,
    alpha: float = 0.05,
    alternative: str = "two-sided",
) -> float:
    """Power of a two-sample z-test for difference of means with shared sigma."""
    if sigma <= 0 or n_per_arm < 2:
        raise ValueError("sigma must be positive and n_per_arm >= 2")
    se = sigma * np.sqrt(2.0 / n_per_arm)
    delta = mu_t - mu_c
    if alternative == "two-sided":
        z = stats.norm.ppf(1 - alpha / 2)
        upper = (z * se - delta) / se
        lower = (-z * se - delta) / se
        return float(stats.norm.sf(upper) + stats.norm.cdf(lower))
    if alternative == "greater":
        z = stats.norm.ppf(1 - alpha)
        return float(stats.norm.sf((z * se - delta) / se))
    if alternative == "less":
        z = stats.norm.ppf(1 - alpha)
        return float(stats.norm.cdf((-z * se - delta) / se))
    raise ValueError(f"unknown alternative: {alternative}")


def required_n(
    mu_c: float,
    mu_t: float,
    sigma: float,
    power: float = 0.8,
    alpha: float = 0.05,
    alternative: str = "two-sided",
    n_max: int = 1_000_000,
) -> int:
    """Smallest per-arm n whose power reaches ``power``."""
    lo, hi = 4, n_max
    if two_sample_z_power(mu_c, mu_t, sigma, hi, alpha, alternative) < power:
        return n_max
    while lo < hi:
        mid = (lo + hi) // 2
        if two_sample_z_power(mu_c, mu_t, sigma, mid, alpha, alternative) >= power:
            hi = mid
        else:
            lo = mid + 1
    return lo


def mde(
    sigma: float,
    n_per_arm: int,
    power: float = 0.8,
    alpha: float = 0.05,
    side: str = "greater",
) -> float:
    """Minimum detectable effect (one-sided) at the given ``n_per_arm``.

    Closed-form: MDE = (z_alpha + z_beta) * sigma * sqrt(2 / n).
    """
    if power <= 0 or power >= 1:
        raise ValueError("power must lie in (0, 1)")
    if sigma <= 0 or n_per_arm < 2:
        raise ValueError("sigma must be positive and n_per_arm >= 2")
    z_a = stats.norm.ppf(1 - alpha) if side in ("greater", "less") else stats.norm.ppf(1 - alpha / 2)
    z_b = stats.norm.ppf(power)
    e = (z_a + z_b) * sigma * np.sqrt(2.0 / n_per_arm)
    return float(e if side != "less" else -e)


def simulate_rejection_rate(
    mu_c: float,
    mu_t: float,
    sigma: float,
    n_per_arm: int,
    alpha: float = 0.05,
    n_experiments: int = 1000,
    seed: int | None = None,
) -> float:
    """Empirical rejection rate via Monte Carlo using Welch's t-test."""
    rng = np.random.default_rng(seed)
    rejects = 0
    for _ in range(n_experiments):
        c = rng.normal(mu_c, sigma, size=n_per_arm)
        t = rng.normal(mu_t, sigma, size=n_per_arm)
        pval = stats.ttest_ind(t, c, equal_var=False).pvalue
        if pval < alpha:
            rejects += 1
    return rejects / n_experiments
