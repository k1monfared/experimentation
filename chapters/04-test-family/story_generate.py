"""Regenerate Chapter 4 (Why don't these tests agree?) story-track figures.

The throughline: multiple procedures look at the same coin data and
produce slightly different answers. Most of the time they agree. At
the boundary, they don't.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.plot.story import PALETTE, apply_story_style, reference_line  # noqa: E402

CHAPTER = "04-test-family"
CHAPTER_DIR = Path(__file__).resolve().parent
IMG_DIR = CHAPTER_DIR / "images" / "story"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.yaml"


def ensure_dirs():
    IMG_DIR.mkdir(parents=True, exist_ok=True)


def load_manifest():
    if MANIFEST_PATH.exists():
        return yaml.safe_load(MANIFEST_PATH.read_text()) or {"artifacts": []}
    return {"artifacts": []}


def save_manifest(m):
    MANIFEST_PATH.write_text(yaml.safe_dump(m, sort_keys=False))


def add_artifact(m, *, path, kind, seed, sha256, description):
    rel = str(path.relative_to(REPO_ROOT))
    m["artifacts"] = [a for a in m["artifacts"] if a.get("path") != rel]
    m["artifacts"].append({
        "path": rel, "chapter": CHAPTER, "kind": kind,
        "seed": seed, "sha256": sha256, "description": description,
    })


# Three procedures we will compare. The names are descriptive in plain English.
def p_exact(k, n):
    """The honest version: count every fair-coin outcome at least as extreme as k."""
    return stats.binomtest(int(k), int(n), p=0.5, alternative="two-sided").pvalue


def p_bell(k, n):
    """The bell-curve approximation: pretend the outcome is normally distributed."""
    if n == 0:
        return 1.0
    p_hat = k / n
    se = np.sqrt(0.5 * 0.5 / n)
    z = (p_hat - 0.5) / se if se > 0 else 0.0
    return float(2 * stats.norm.sf(abs(z)))


def p_proxy(k, n, ref_size=None):
    """The 'proxy crowd' procedure (Fisher's exact, force-fitted to one sample).

    Pair the observation (k heads, n-k tails) with a reference 'fair crowd'
    of size ref_size that came up exactly half heads. Run a 2x2 test.
    Default reference size is n, which makes Fisher conservative.
    """
    if ref_size is None:
        ref_size = n
    half = ref_size / 2
    # Some odd ref_size cases need rounding
    table = [[int(k), int(n - k)], [int(round(half)), int(round(half))]]
    # Fisher exact requires non-negative ints
    return float(stats.fisher_exact(table)[1])


def render_same_data_three_views():
    """One observation, three procedures, three p-values."""
    apply_story_style()
    cases = [(6, 10), (60, 100), (600, 1000)]
    procedures = ["honest count", "bell-curve approximation", "proxy-crowd procedure"]
    fig, axes = plt.subplots(1, len(cases), figsize=(13, 4.0), sharey=True)
    for ax, (k, n) in zip(axes, cases):
        vals = [p_exact(k, n), p_bell(k, n), p_proxy(k, n)]
        colors = [PALETTE["focus"], PALETTE["contrast"], PALETTE["support"]]
        bars = ax.bar(np.arange(len(procedures)), vals, color=colors, width=0.7)
        for i, (v, b) in enumerate(zip(vals, bars)):
            label = f"{v:.3f}" if v >= 1e-3 else f"{v:.1e}"
            ax.text(i, max(v, 0.001) * 1.05, label, ha="center", fontsize=9)
        ax.axhline(0.05, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.set_xticks(np.arange(len(procedures)))
        ax.set_xticklabels(procedures, rotation=20, fontsize=8)
        ax.set_yscale("log")
        ax.set_ylim(1e-12, 2)
        ax.set_title(f"observation: {k} heads in {n} tosses")
        if ax is axes[0]:
            ax.set_ylabel("p-value (log scale)")
    out = IMG_DIR / "same_data_three_views.png"
    fig.savefig(out)
    plt.close(fig)
    return out, [(k, n, p_exact(k, n), p_bell(k, n), p_proxy(k, n)) for k, n in cases]


def render_bell_vs_honest_gap():
    """How big is the gap between honest count and bell-curve approximation as N grows?"""
    apply_story_style()
    sizes = [10, 25, 50, 100, 250, 500, 1000]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for n, color in zip(sizes, [PALETTE["focus"], PALETTE["contrast"], PALETTE["support"],
                                 "#7a9b76", PALETTE["ink"], PALETTE["muted"], "#9a6f9c"]):
        # Compute the gap across every possible k from 0 to n
        gaps = []
        ks = np.arange(0, n + 1)
        for k in ks:
            gaps.append(abs(p_exact(k, n) - p_bell(k, n)))
        gaps = np.array(gaps)
        ax.plot(ks / n, gaps, color=color, linewidth=1.6, label=f"n = {n}")
    ax.set_xlabel("observed fraction (heads / tosses)")
    ax.set_ylabel("gap between honest count and bell-curve approximation")
    ax.set_xlim(0, 1)
    ax.legend(loc="upper right", title="number of tosses")
    out = IMG_DIR / "bell_vs_honest_gap.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_boundary_breakdown():
    """At extreme observations (0/n, n/n) what do the procedures do?"""
    apply_story_style()
    # 0/10, 10/10, 0/100, 100/100, 1/1
    obs = [(1, 1), (0, 10), (10, 10), (0, 100), (100, 100)]
    labels = [f"{k}/{n}" for k, n in obs]
    procedures = ["honest count", "bell-curve approximation", "proxy-crowd procedure"]

    p_grid = np.zeros((len(procedures), len(obs)))
    for j, (k, n) in enumerate(obs):
        try:
            p_grid[0, j] = p_exact(k, n)
        except Exception:
            p_grid[0, j] = np.nan
        try:
            p_grid[1, j] = p_bell(k, n)
        except Exception:
            p_grid[1, j] = np.nan
        try:
            p_grid[2, j] = p_proxy(k, n)
        except Exception:
            p_grid[2, j] = np.nan

    fig, ax = plt.subplots(figsize=(11, 4.5))
    width = 0.27
    x = np.arange(len(obs))
    for i, (proc, color) in enumerate(zip(
        procedures, [PALETTE["focus"], PALETTE["contrast"], PALETTE["support"]]
    )):
        # Plot p-values; clamp very small to a floor so log scale shows them
        vals = np.array([max(v, 1e-30) if not np.isnan(v) else 1e-30 for v in p_grid[i]])
        ax.bar(x + (i - 1) * width, vals, width=width, color=color, label=proc)
    ax.axhline(0.05, color=PALETTE["muted"], linestyle="--", linewidth=1, label="alpha = 0.05")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_yscale("log")
    ax.set_ylim(1e-30, 5)
    ax.set_xlabel("observation")
    ax.set_ylabel("p-value (log scale)")
    ax.legend(loc="lower right", fontsize=8)
    out = IMG_DIR / "boundary_breakdown.png"
    fig.savefig(out)
    plt.close(fig)
    return out, p_grid


def render_belief_alongside():
    """The Bayesian view of the same observations, side by side."""
    apply_story_style()
    cases = [(6, 10), (60, 100), (600, 1000)]
    fig, axes = plt.subplots(1, len(cases), figsize=(13, 4.0), sharey=False)
    ps = np.linspace(0, 1, 1000)
    for ax, (k, n) in zip(axes, cases):
        a, b = 1 + k, 1 + n - k
        density = stats.beta.pdf(ps, a, b)
        ax.fill_between(ps, 0, density, color=PALETTE["focus"], alpha=0.3)
        ax.plot(ps, density, color=PALETTE["focus"], linewidth=2)
        ax.axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1, label="fair = 0.5")
        lo = stats.beta.ppf(0.025, a, b)
        hi = stats.beta.ppf(0.975, a, b)
        ax.axvline(lo, color=PALETTE["ink"], linestyle=":", linewidth=0.8)
        ax.axvline(hi, color=PALETTE["ink"], linestyle=":", linewidth=0.8)
        ax.set_xlim(0, 1)
        ax.set_xlabel("possible bias of the coin")
        ax.set_ylabel("how strongly I believe each value")
        ax.set_title(f"after seeing {k}/{n}\n95% band [{lo:.3f}, {hi:.3f}]")
        if ax is axes[0]:
            ax.legend()
    out = IMG_DIR / "belief_alongside.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    paths = []
    p_three, vals = render_same_data_three_views()
    paths.append((p_three, "derived",
                  f"Story Ch.4: same observation through three procedures (6/10, 60/100, 600/1000): {[(k, n, round(e, 4), round(b, 4), round(f, 4)) for k, n, e, b, f in vals]}"))
    paths.append((render_bell_vs_honest_gap(), "derived",
                  "Story Ch.4: gap between honest count and bell-curve approx as N grows"))
    p_bd, _ = render_boundary_breakdown()
    paths.append((p_bd, "derived",
                  "Story Ch.4: what each procedure does at boundary observations (0/10, 10/10, 1/1, etc.)"))
    paths.append((render_belief_alongside(), "derived",
                  "Story Ch.4: Bayesian view alongside, three observations of the same fraction at different N"))
    print(f"Story Ch.4: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
