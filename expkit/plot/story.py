"""Modern, friendly chart style for the story track.

Distinct from ``expkit.plot.style`` (the technical track). Story figures
are drawn for a non-technical reader: warmer palette, larger axis
labels, no chart border, generous whitespace. Helpers also enforce
statistical hygiene: bar charts always start at zero on the y-axis,
no pie-chart helpers (use bars instead).

Usage in a chapter's ``story_generate.py``::

    from expkit.plot.story import PALETTE, apply_story_style, bars, coin_strip
    apply_story_style()
    fig, ax = plt.subplots()
    ...
"""

from __future__ import annotations

from typing import Iterable

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


# Modern friendly palette. One warm focus color, one cool contrast,
# muted neutrals. Tested against journal-paper red/blue/green to feel
# less clinical without losing accessibility.
PALETTE = {
    "ink": "#1f1d2c",        # near-black, main text and lines
    "focus": "#c4574b",      # warm terracotta, the "this is the thing" color
    "contrast": "#3d6b8a",   # cool ink-blue, secondary
    "support": "#d5a059",    # soft gold, tertiary highlight
    "muted": "#9a9aa3",      # cool gray, reference lines and reduced-attention items
    "soft": "#e9e5da",       # warm cream, fills and tail markers
    "rule": "#cfcfd3",       # very light gray, gridlines
    "ghost": "#e6e0d3",      # softer cream, for context lines under the focus line
}

# Color sequence for plots with several lines. Picked so each color
# stands on its own and against the page background.
SEQUENCE = [
    PALETTE["focus"],
    PALETTE["contrast"],
    PALETTE["support"],
    PALETTE["ink"],
    "#7a9b76",   # muted sage
    "#9a6f9c",   # muted plum
]


def apply_story_style() -> None:
    """Set matplotlib rcParams for the story track. Idempotent."""
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica", "Liberation Sans"],
        "font.size": 12,
        "axes.titlesize": 13,
        "axes.titleweight": "regular",
        "axes.titlecolor": PALETTE["ink"],
        "axes.labelsize": 11,
        "axes.labelcolor": PALETTE["ink"],
        "axes.edgecolor": PALETTE["muted"],
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "xtick.color": PALETTE["ink"],
        "ytick.color": PALETTE["ink"],
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "grid.color": PALETTE["rule"],
        "grid.linewidth": 0.5,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "lines.linewidth": 1.6,
        "patch.edgecolor": "none",
        "legend.frameon": False,
        "legend.fontsize": 10,
        "legend.loc": "best",
        "savefig.dpi": 144,
        "savefig.bbox": "tight",
        "figure.constrained_layout.use": True,
    })


def bars(ax, labels, values, *, color=None, label=None, base_zero=True, allow_negative=False):
    """Draw a bar chart. Always starts the y-axis at zero unless explicitly opted out.

    Statistical hygiene rule: cropping the y-axis on a bar chart
    visually inflates differences. We do not let that happen by default.

    Set ``allow_negative=True`` only when the data really does include
    signed values (e.g. lifts, differences) that need a zero baseline
    in the middle.
    """
    if color is None:
        color = PALETTE["focus"]
    arr = np.asarray(values, dtype=float)
    rect = ax.bar(labels, arr, color=color, label=label)
    if not base_zero:
        return rect
    top = float(arr.max())
    bottom = float(arr.min())
    if not allow_negative and bottom < 0:
        raise ValueError(
            "bars() got negative values; pass allow_negative=True if intended"
        )
    span = max(top, 0.0) - min(bottom, 0.0)
    pad = 0.08 * span if span > 0 else max(abs(top), 1.0) * 0.08
    if bottom >= 0:
        ax.set_ylim(0, top + pad)
    else:
        ax.set_ylim(bottom - pad, top + pad)
        ax.axhline(0, color=PALETTE["muted"], linewidth=0.8)
    return rect


def coin_strip(ax, sequence: Iterable[int], *, head_color=None, tail_color=None, label_letters: bool = True):
    """Render a sequence of 0/1 tosses as a horizontal strip of cells.

    A friendlier visual than text 'HHTHTH' for short sequences.
    1 = head (filled focus color), 0 = tail (cream fill).
    """
    if head_color is None:
        head_color = PALETTE["focus"]
    if tail_color is None:
        tail_color = PALETTE["soft"]
    seq = np.asarray(list(sequence))
    n = len(seq)
    for i, s in enumerate(seq):
        ax.add_patch(plt.Rectangle(
            (i + 0.04, 0.04), 0.92, 0.92,
            facecolor=head_color if s else tail_color,
            edgecolor=PALETTE["ink"], linewidth=0.7,
        ))
        if label_letters:
            txt = "H" if s else "T"
            ax.text(
                i + 0.5, 0.5, txt,
                ha="center", va="center",
                color="white" if s else PALETTE["ink"],
                fontsize=12, fontweight="bold",
            )
    ax.set_xlim(0, n)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ("top", "right", "left", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.grid(False)


def reference_line(ax, y, *, label=None, color=None, linestyle="--", linewidth=1.0):
    """Light reference line, e.g. y=0.5 for the fair-coin reference."""
    if color is None:
        color = PALETTE["muted"]
    return ax.axhline(y, color=color, linestyle=linestyle, linewidth=linewidth, label=label, zorder=1)


def soft_band(ax, x, lo, hi, *, color=None, alpha=0.18):
    """Translucent band between lo and hi over x. For uncertainty regions."""
    if color is None:
        color = PALETTE["focus"]
    ax.fill_between(x, lo, hi, color=color, alpha=alpha, linewidth=0)


def annotate_point(ax, x, y, text, *, dx=8, dy=8, color=None):
    """Small annotation arrow with text. Used for "this is the thing" markers."""
    if color is None:
        color = PALETTE["ink"]
    ax.annotate(
        text,
        xy=(x, y), xytext=(dx, dy), textcoords="offset points",
        fontsize=10, color=color,
        arrowprops=dict(arrowstyle="-", color=PALETTE["muted"], lw=0.8),
    )
