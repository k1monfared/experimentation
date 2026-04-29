"""Two-arm A/B test simulators."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class TwoArmBinary:
    control: np.ndarray
    treatment: np.ndarray
    p_control: float
    p_treatment: float


@dataclass(frozen=True)
class TwoArmContinuous:
    control: np.ndarray
    treatment: np.ndarray
    mu_control: float
    mu_treatment: float
    sigma: float


def two_arm_binary(
    n_per_arm: int,
    p_control: float,
    p_treatment: float,
    seed: int | None = None,
) -> TwoArmBinary:
    """Simulate a binary outcome two-arm experiment with equal arm sizes."""
    rng = np.random.default_rng(seed)
    c = rng.binomial(1, p_control, size=n_per_arm)
    t = rng.binomial(1, p_treatment, size=n_per_arm)
    return TwoArmBinary(control=c, treatment=t, p_control=p_control, p_treatment=p_treatment)


def two_arm_continuous(
    n_per_arm: int,
    mu_control: float,
    mu_treatment: float,
    sigma: float = 1.0,
    seed: int | None = None,
) -> TwoArmContinuous:
    """Simulate a continuous-outcome two-arm experiment with normal noise."""
    rng = np.random.default_rng(seed)
    c = rng.normal(mu_control, sigma, size=n_per_arm)
    t = rng.normal(mu_treatment, sigma, size=n_per_arm)
    return TwoArmContinuous(control=c, treatment=t, mu_control=mu_control, mu_treatment=mu_treatment, sigma=sigma)


def stratified_binary(
    strata_sizes: dict[str, int],
    p_by_stratum: dict[str, tuple[float, float]],
    seed: int | None = None,
) -> dict[str, TwoArmBinary]:
    """Simulate per-stratum binary experiments. Returns a dict keyed by stratum.

    ``p_by_stratum`` maps stratum name to ``(p_control, p_treatment)``.
    Both dicts must have the same keys.
    """
    if set(strata_sizes) != set(p_by_stratum):
        raise ValueError("strata_sizes and p_by_stratum must have the same keys")
    rng = np.random.default_rng(seed)
    out = {}
    for name in strata_sizes:
        n = strata_sizes[name]
        pc, pt = p_by_stratum[name]
        sub_seed = int(rng.integers(0, 2**31 - 1))
        out[name] = two_arm_binary(n, pc, pt, seed=sub_seed)
    return out
