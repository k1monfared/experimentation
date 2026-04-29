"""Power, sample size, and minimum detectable effect for binomial tests."""

from __future__ import annotations

import numpy as np
from scipy import stats


def normal_approx_power(
    p_null: float,
    p_alt: float,
    n: int,
    alpha: float = 0.05,
    alternative: str = "two-sided",
) -> float:
    """Normal-approximation power for a one-sample proportion test.

    Returns P(reject H0 | true probability is ``p_alt``).
    """
    if not 0.0 < p_null < 1.0 or not 0.0 < p_alt < 1.0:
        raise ValueError("p_null and p_alt must be in (0, 1)")
    se_null = np.sqrt(p_null * (1 - p_null) / n)
    se_alt = np.sqrt(p_alt * (1 - p_alt) / n)
    if alternative == "two-sided":
        z = stats.norm.ppf(1 - alpha / 2)
        upper = (p_null + z * se_null - p_alt) / se_alt
        lower = (p_null - z * se_null - p_alt) / se_alt
        return float(stats.norm.sf(upper) + stats.norm.cdf(lower))
    if alternative == "greater":
        z = stats.norm.ppf(1 - alpha)
        return float(stats.norm.sf((p_null + z * se_null - p_alt) / se_alt))
    if alternative == "less":
        z = stats.norm.ppf(1 - alpha)
        return float(stats.norm.cdf((p_null - z * se_null - p_alt) / se_alt))
    raise ValueError(f"unknown alternative: {alternative}")


def required_n(
    p_null: float,
    p_alt: float,
    power: float = 0.8,
    alpha: float = 0.05,
    alternative: str = "two-sided",
    n_max: int = 1_000_000,
) -> int:
    """Smallest ``n`` whose normal-approx power reaches ``power``.

    Returns ``n_max`` if the target is not reached.
    """
    lo, hi = 4, n_max
    if normal_approx_power(p_null, p_alt, hi, alpha, alternative) < power:
        return n_max
    while lo < hi:
        mid = (lo + hi) // 2
        if normal_approx_power(p_null, p_alt, mid, alpha, alternative) >= power:
            hi = mid
        else:
            lo = mid + 1
    return lo


def mde(
    p_null: float,
    n: int,
    power: float = 0.8,
    alpha: float = 0.05,
    side: str = "greater",
    grid: int = 2001,
) -> float:
    """Minimum detectable effect (one-sided) at the given ``n`` and ``power``.

    Returns the smallest ``|p_alt - p_null|`` such that power >= target.
    """
    if side == "greater":
        candidates = np.linspace(p_null + 1e-4, 0.999, grid)
        powers = np.array([normal_approx_power(p_null, p, n, alpha, "greater") for p in candidates])
    elif side == "less":
        candidates = np.linspace(0.001, p_null - 1e-4, grid)
        powers = np.array([normal_approx_power(p_null, p, n, alpha, "less") for p in candidates])
    else:
        raise ValueError("side must be 'greater' or 'less'")
    ok = np.where(powers >= power)[0]
    if len(ok) == 0:
        return float("nan")
    idx = ok.min() if side == "greater" else ok.max()
    return float(abs(candidates[idx] - p_null))


def simulate_rejection_rate(
    p_true: float,
    n: int,
    p_null: float = 0.5,
    alpha: float = 0.05,
    n_experiments: int = 1000,
    seed: int | None = None,
) -> float:
    """Empirical rejection rate via Monte Carlo simulation.

    For each of ``n_experiments`` synthetic samples of size ``n`` drawn from
    Bernoulli(``p_true``), runs an exact two-sided binomial test against
    ``p_null`` and records whether ``p < alpha``. Returns the fraction
    rejected.
    """
    rng = np.random.default_rng(seed)
    counts = rng.binomial(n, p_true, size=n_experiments)
    rejects = 0
    for k in counts:
        pval = stats.binomtest(int(k), n, p=p_null).pvalue
        if pval < alpha:
            rejects += 1
    return rejects / n_experiments
