"""Shared matplotlib defaults used across chapters."""

from __future__ import annotations

import matplotlib as mpl


PALETTE = {
    "frequentist": "#1f77b4",
    "bayesian": "#d62728",
    "neutral": "#444444",
    "highlight": "#2ca02c",
    "muted": "#888888",
}


def apply_style() -> None:
    """Apply project-wide matplotlib defaults. Idempotent."""
    mpl.rcParams.update(
        {
            "figure.figsize": (8.0, 4.5),
            "figure.dpi": 110,
            "savefig.dpi": 150,
            "savefig.bbox": "tight",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "legend.frameon": False,
            "legend.fontsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "lines.linewidth": 1.6,
            "grid.alpha": 0.3,
            "grid.linestyle": "-",
        }
    )
