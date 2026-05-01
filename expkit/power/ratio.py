"""Power, sample size, and MDE for ratio metrics under the delta method.

Two-arm setting where the metric of interest is a ratio ``R = mean(N) / mean(D)``
(e.g. clicks per session, revenue per visitor). The delta method gives an
approximate per-unit variance for ``R``:

    var_unit = sigma_n**2 / mu_d**2
              + (mu_n**2 / mu_d**4) * sigma_d**2
              - 2 * (mu_n / mu_d**3) * cov_nd

The estimator's variance for a sample of ``n_per_arm`` units is ``var_unit /
n_per_arm`` per arm; for a difference between two arms (independent samples
with the same per-unit variance) the standard error is
``sqrt(2 * var_unit / n_per_arm)``. From there, the formulas mirror the
continuous two-sample case: substitute the delta-method ``sigma_eff =
sqrt(var_unit)`` for the simple-mean ``sigma`` and reuse the same z-test
machinery.

If you already have an effective per-unit standard deviation ``sigma_eff`` for
your ratio (e.g. from a pilot study or from
``expkit.metrics.delta.ratio_mean_and_var``), pass it directly via
``sigma_eff``. Otherwise pass the underlying first and second moments via the
``mu_n``, ``mu_d``, ``sigma_n``, ``sigma_d``, ``cov_nd`` parameters and let
this module compute it.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def delta_sigma(
    mu_n: float,
    mu_d: float,
    sigma_n: float,
    sigma_d: float,
    cov_nd: float = 0.0,
) -> float:
    """Effective per-unit standard deviation of a ratio estimator via delta method."""
    if mu_d == 0:
        raise ValueError("mu_d (mean of denominator) must be nonzero")
    if sigma_n < 0 or sigma_d < 0:
        raise ValueError("sigma_n and sigma_d must be non-negative")
    var_unit = (
        sigma_n ** 2 / mu_d ** 2
        + (mu_n ** 2 / mu_d ** 4) * sigma_d ** 2
        - 2.0 * (mu_n / mu_d ** 3) * cov_nd
    )
    if var_unit < 0:
        raise ValueError(
            "delta-method variance came out negative; check that cov_nd is "
            "consistent with sigma_n, sigma_d (|cov| <= sigma_n * sigma_d)"
        )
    return float(np.sqrt(var_unit))


def _resolve_sigma(
    sigma_eff: float | None,
    mu_n: float | None,
    mu_d: float | None,
    sigma_n: float | None,
    sigma_d: float | None,
    cov_nd: float,
) -> float:
    if sigma_eff is not None:
        if sigma_eff <= 0:
            raise ValueError("sigma_eff must be positive")
        return float(sigma_eff)
    if None in (mu_n, mu_d, sigma_n, sigma_d):
        raise ValueError(
            "either pass sigma_eff, or pass all of mu_n, mu_d, sigma_n, sigma_d"
        )
    return delta_sigma(mu_n, mu_d, sigma_n, sigma_d, cov_nd)


def two_arm_z_power(
    diff: float,
    n_per_arm: int,
    sigma_eff: float | None = None,
    *,
    mu_n: float | None = None,
    mu_d: float | None = None,
    sigma_n: float | None = None,
    sigma_d: float | None = None,
    cov_nd: float = 0.0,
    alpha: float = 0.05,
    alternative: str = "two-sided",
) -> float:
    """Power of a two-arm z-test on a ratio metric, given effect size ``diff``.

    ``diff`` is the assumed true difference in ratios (treatment minus control).
    Either pass ``sigma_eff`` (delta-method per-unit SD) or the underlying
    moments and this function will derive it.
    """
    if n_per_arm < 2:
        raise ValueError("n_per_arm must be >= 2")
    s = _resolve_sigma(sigma_eff, mu_n, mu_d, sigma_n, sigma_d, cov_nd)
    se = s * np.sqrt(2.0 / n_per_arm)
    if alternative == "two-sided":
        z = stats.norm.ppf(1 - alpha / 2)
        upper = (z * se - diff) / se
        lower = (-z * se - diff) / se
        return float(stats.norm.sf(upper) + stats.norm.cdf(lower))
    if alternative == "greater":
        z = stats.norm.ppf(1 - alpha)
        return float(stats.norm.sf((z * se - diff) / se))
    if alternative == "less":
        z = stats.norm.ppf(1 - alpha)
        return float(stats.norm.cdf((-z * se - diff) / se))
    raise ValueError(f"unknown alternative: {alternative}")


def required_n(
    diff: float,
    sigma_eff: float | None = None,
    *,
    mu_n: float | None = None,
    mu_d: float | None = None,
    sigma_n: float | None = None,
    sigma_d: float | None = None,
    cov_nd: float = 0.0,
    power: float = 0.8,
    alpha: float = 0.05,
    alternative: str = "two-sided",
    n_max: int = 1_000_000,
) -> int:
    """Smallest per-arm sample size whose power reaches ``power``."""
    s = _resolve_sigma(sigma_eff, mu_n, mu_d, sigma_n, sigma_d, cov_nd)
    lo, hi = 4, n_max
    if two_arm_z_power(diff, hi, sigma_eff=s, alpha=alpha, alternative=alternative) < power:
        return n_max
    while lo < hi:
        mid = (lo + hi) // 2
        p = two_arm_z_power(diff, mid, sigma_eff=s, alpha=alpha, alternative=alternative)
        if p >= power:
            hi = mid
        else:
            lo = mid + 1
    return lo


def mde(
    n_per_arm: int,
    sigma_eff: float | None = None,
    *,
    mu_n: float | None = None,
    mu_d: float | None = None,
    sigma_n: float | None = None,
    sigma_d: float | None = None,
    cov_nd: float = 0.0,
    power: float = 0.8,
    alpha: float = 0.05,
    side: str = "greater",
) -> float:
    """Minimum detectable difference in ratios at the given ``n_per_arm``.

    Closed-form: MDE = (z_alpha + z_beta) * sigma_eff * sqrt(2 / n_per_arm).
    """
    if power <= 0 or power >= 1:
        raise ValueError("power must lie in (0, 1)")
    if n_per_arm < 2:
        raise ValueError("n_per_arm must be >= 2")
    s = _resolve_sigma(sigma_eff, mu_n, mu_d, sigma_n, sigma_d, cov_nd)
    z_a = (
        stats.norm.ppf(1 - alpha)
        if side in ("greater", "less")
        else stats.norm.ppf(1 - alpha / 2)
    )
    z_b = stats.norm.ppf(power)
    e = (z_a + z_b) * s * np.sqrt(2.0 / n_per_arm)
    return float(e if side != "less" else -e)


def simulate_rejection_rate(
    diff: float,
    n_per_arm: int,
    sigma_eff: float,
    alpha: float = 0.05,
    n_experiments: int = 1000,
    seed: int | None = None,
) -> float:
    """Empirical rejection rate, treating the ratio estimator as Normal.

    This validates the closed-form ``two_arm_z_power`` against Monte Carlo when
    the delta-method approximation is exact (Normal estimators with known
    per-unit variance ``sigma_eff**2``). Real ratio metrics will deviate when
    the sample size is small or the denominator can be near zero.
    """
    if sigma_eff <= 0:
        raise ValueError("sigma_eff must be positive")
    rng = np.random.default_rng(seed)
    se = sigma_eff * np.sqrt(2.0 / n_per_arm)
    z_crit = stats.norm.ppf(1 - alpha / 2)
    diffs = rng.normal(loc=diff, scale=se, size=n_experiments)
    rejects = np.abs(diffs / se) > z_crit
    return float(rejects.mean())
