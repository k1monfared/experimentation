"""Reusable diagnostic plots for chapters."""

from __future__ import annotations

from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np

from expkit.inference.binomial import running_wilson_band
from expkit.plot.style import PALETTE, apply_style
from expkit.sim.coin import running_fraction


def plot_running_fraction(
    seq: np.ndarray,
    ax: plt.Axes | None = None,
    show_truth: float | None = 0.5,
    label: str | None = None,
    color: str | None = None,
) -> plt.Axes:
    """Plot the running fraction of heads across a Bernoulli sequence."""
    apply_style()
    if ax is None:
        _, ax = plt.subplots()
    frac = running_fraction(seq)
    n = len(seq)
    color = color or PALETTE["frequentist"]
    ax.plot(np.arange(1, n + 1), frac, color=color, label=label or "running fraction")
    if show_truth is not None:
        ax.axhline(show_truth, color=PALETTE["muted"], linestyle="--", linewidth=1, label=f"true p = {show_truth:.2f}")
    ax.set_xlabel("toss number")
    ax.set_ylabel("fraction of heads so far")
    ax.set_ylim(0.0, 1.0)
    ax.set_xscale("log") if n >= 1000 else ax.set_xscale("linear")
    ax.legend(loc="best")
    return ax


def plot_running_fraction_with_band(
    seq: np.ndarray,
    ax: plt.Axes | None = None,
    show_truth: float | None = 0.5,
    alpha: float = 0.05,
    color: str | None = None,
) -> plt.Axes:
    """Running fraction overlaid with a Wilson confidence band."""
    apply_style()
    if ax is None:
        _, ax = plt.subplots()
    frac = running_fraction(seq)
    lows, highs = running_wilson_band(seq, alpha=alpha)
    n = len(seq)
    xs = np.arange(1, n + 1)
    color = color or PALETTE["frequentist"]
    ax.plot(xs, frac, color=color, label="running fraction")
    ax.fill_between(xs, lows, highs, color=color, alpha=0.18, label=f"{int((1 - alpha) * 100)}% Wilson CI")
    if show_truth is not None:
        ax.axhline(show_truth, color=PALETTE["muted"], linestyle="--", linewidth=1, label=f"true p = {show_truth:.2f}")
    ax.set_xlabel("toss number")
    ax.set_ylabel("fraction of heads")
    ax.set_ylim(0.0, 1.0)
    if n >= 1000:
        ax.set_xscale("log")
    ax.legend(loc="best")
    return ax


def plot_posterior(
    idata,
    ax: plt.Axes | None = None,
    truth: float | None = 0.5,
    color: str | None = None,
    label: str | None = None,
    bins: int = 60,
) -> plt.Axes:
    """Histogram of the posterior on ``p`` from a PyMC InferenceData object."""
    apply_style()
    if ax is None:
        _, ax = plt.subplots()
    p_samples = idata.posterior["p"].values.ravel()
    color = color or PALETTE["bayesian"]
    ax.hist(p_samples, bins=bins, density=True, color=color, alpha=0.55, label=label or "posterior on p")
    if truth is not None:
        ax.axvline(truth, color=PALETTE["muted"], linestyle="--", linewidth=1, label=f"true p = {truth:.2f}")
    ax.set_xlabel("p")
    ax.set_ylabel("posterior density")
    ax.set_xlim(0.0, 1.0)
    ax.legend(loc="best")
    return ax


def plot_posterior_sequence(
    idata_snapshots: Sequence,
    ns: Iterable[int],
    ax: plt.Axes | None = None,
    truth: float | None = 0.5,
    bins: int = 60,
) -> plt.Axes:
    """Overlay posteriors taken at increasing sample sizes to show tightening."""
    apply_style()
    if ax is None:
        _, ax = plt.subplots()
    cmap = plt.get_cmap("viridis")
    snapshots = list(idata_snapshots)
    n_list = list(ns)
    for i, (idata, n) in enumerate(zip(snapshots, n_list)):
        p_samples = idata.posterior["p"].values.ravel()
        color = cmap(i / max(1, len(snapshots) - 1))
        ax.hist(
            p_samples,
            bins=bins,
            density=True,
            color=color,
            alpha=0.45,
            label=f"N = {n}",
            histtype="stepfilled",
        )
    if truth is not None:
        ax.axvline(truth, color=PALETTE["muted"], linestyle="--", linewidth=1, label=f"true p = {truth:.2f}")
    ax.set_xlabel("p")
    ax.set_ylabel("posterior density")
    ax.set_xlim(0.0, 1.0)
    ax.legend(loc="best", ncols=2)
    return ax
