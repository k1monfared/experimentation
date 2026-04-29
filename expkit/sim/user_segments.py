"""Heterogeneous user populations and segmented A/B simulators."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SegmentSpec:
    name: str
    fraction: float
    baseline: float
    treatment_lift: float


@dataclass(frozen=True)
class SegmentedExperiment:
    segments: dict[str, np.ndarray]  # segment name -> {"control": arr, "treatment": arr}
    specs: list[SegmentSpec]


def segmented_binary(
    n_total: int,
    specs: list[SegmentSpec],
    treatment_share: float = 0.5,
    seed: int | None = None,
) -> dict[str, dict[str, np.ndarray]]:
    """Simulate a binary-outcome A/B with heterogeneous segments.

    Returns a dict keyed by segment name with arrays for control and treatment
    arms within that segment. Total sample size sums to ``n_total``.
    """
    if not np.isclose(sum(s.fraction for s in specs), 1.0):
        raise ValueError("segment fractions must sum to 1.0")
    rng = np.random.default_rng(seed)
    out: dict[str, dict[str, np.ndarray]] = {}
    for spec in specs:
        n_seg = int(round(n_total * spec.fraction))
        n_treat = int(round(n_seg * treatment_share))
        n_control = n_seg - n_treat
        c = rng.binomial(1, spec.baseline, size=n_control)
        t = rng.binomial(1, np.clip(spec.baseline + spec.treatment_lift, 0.0, 1.0), size=n_treat)
        out[spec.name] = {"control": c, "treatment": t}
    return out


def imbalanced_assignment(
    n_total: int,
    specs: list[SegmentSpec],
    treatment_share_by_segment: dict[str, float],
    seed: int | None = None,
) -> dict[str, dict[str, np.ndarray]]:
    """Same as ``segmented_binary`` but with per-segment imbalance in assignment.

    Useful for constructing Simpson's-paradox examples.
    """
    rng = np.random.default_rng(seed)
    out: dict[str, dict[str, np.ndarray]] = {}
    for spec in specs:
        n_seg = int(round(n_total * spec.fraction))
        share = treatment_share_by_segment[spec.name]
        n_treat = int(round(n_seg * share))
        n_control = n_seg - n_treat
        c = rng.binomial(1, spec.baseline, size=n_control)
        t = rng.binomial(1, np.clip(spec.baseline + spec.treatment_lift, 0.0, 1.0), size=n_treat)
        out[spec.name] = {"control": c, "treatment": t}
    return out
