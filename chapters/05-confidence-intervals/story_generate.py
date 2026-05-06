"""Regenerate Chapter 5 (What range is the bias plausibly in?) figures.

Build interval procedures slowly: from a single observation through
several different ways of drawing the interval, then a coverage
simulation that shows which procedures actually deliver what they
promise.
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

CHAPTER = "05-confidence-intervals"
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


def wald_ci(k, n, level=0.95):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    z = stats.norm.ppf((1 + level) / 2)
    se = np.sqrt(p * (1 - p) / n)
    return (max(0, p - z * se), min(1, p + z * se))


def wilson_ci(k, n, level=0.95):
    if n == 0:
        return (0.0, 1.0)
    z = stats.norm.ppf((1 + level) / 2)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0, centre - half), min(1, centre + half))


def clopper_pearson_ci(k, n, level=0.95):
    alpha = 1 - level
    lo = stats.beta.ppf(alpha / 2, k, n - k + 1) if k > 0 else 0.0
    hi = stats.beta.ppf(1 - alpha / 2, k + 1, n - k) if k < n else 1.0
    return (lo, hi)


def bayesian_ci(k, n, level=0.95, a=1, b=1):
    alpha = 1 - level
    lo = stats.beta.ppf(alpha / 2, a + k, b + n - k)
    hi = stats.beta.ppf(1 - alpha / 2, a + k, b + n - k)
    return (lo, hi)


def render_intervals_at_observations():
    """Several procedures applied to the same observation, side by side."""
    apply_story_style()
    cases = [(6, 10), (60, 100), (600, 1000)]
    procedures = [
        ("simple bell-curve interval", wald_ci, PALETTE["focus"]),
        ("shrunken-centre interval", wilson_ci, PALETTE["contrast"]),
        ("guaranteed-coverage interval", clopper_pearson_ci, PALETTE["support"]),
        ("belief-curve interval", bayesian_ci, "#7a9b76"),
    ]
    fig, axes = plt.subplots(1, len(cases), figsize=(13, 4.0), sharey=True)
    for ax, (k, n) in zip(axes, cases):
        for i, (name, fn, color) in enumerate(procedures):
            lo, hi = fn(k, n)
            y = len(procedures) - i
            ax.plot([lo, hi], [y, y], color=color, linewidth=4, alpha=0.85)
            ax.scatter([lo, hi], [y, y], color=color, s=40, zorder=3)
            ax.text(0.02, y, name, fontsize=9, ha="left", va="center", color=color)
        ax.axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, len(procedures) + 1)
        ax.set_yticks([])
        ax.set_xlabel("possible bias of the coin")
        ax.set_title(f"observation: {k} heads in {n} tosses")
    out = IMG_DIR / "intervals_at_observations.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_boundary_failures():
    """At 0/10 and 10/10, watch the procedures behave."""
    apply_story_style()
    cases = [(0, 10), (10, 10), (1, 100), (99, 100)]
    procedures = [
        ("simple bell-curve interval", wald_ci, PALETTE["focus"]),
        ("shrunken-centre interval", wilson_ci, PALETTE["contrast"]),
        ("guaranteed-coverage interval", clopper_pearson_ci, PALETTE["support"]),
        ("belief-curve interval", bayesian_ci, "#7a9b76"),
    ]
    fig, axes = plt.subplots(1, len(cases), figsize=(15, 4.0), sharey=True)
    for ax, (k, n) in zip(axes, cases):
        for i, (name, fn, color) in enumerate(procedures):
            lo, hi = fn(k, n)
            y = len(procedures) - i
            if hi - lo < 1e-6:
                # degenerate point interval: draw as a dot
                ax.scatter([lo], [y], color=color, s=80, zorder=3)
                ax.text(lo + 0.02, y, "(point)", fontsize=8, color=color, va="center")
            else:
                ax.plot([lo, hi], [y, y], color=color, linewidth=4, alpha=0.85)
                ax.scatter([lo, hi], [y, y], color=color, s=40, zorder=3)
            ax.text(0.02, y - 0.4, name, fontsize=8, ha="left", va="center", color=color)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, len(procedures) + 1)
        ax.set_yticks([])
        ax.set_xlabel("possible bias")
        ax.set_title(f"{k}/{n}")
    out = IMG_DIR / "boundary_failures.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_coverage_at_p_50():
    """Across many simulated experiments at p=0.5, how often does each interval contain 0.5?"""
    apply_story_style()
    rng = np.random.default_rng(123)
    sizes = [5, 10, 20, 50, 100]
    n_trials = 5000
    rates = {name: [] for name in ["Wald", "Wilson", "Clopper-Pearson", "Belief"]}
    for n in sizes:
        ks = rng.binomial(n, 0.5, size=n_trials)
        for name, fn in [("Wald", wald_ci), ("Wilson", wilson_ci),
                         ("Clopper-Pearson", clopper_pearson_ci), ("Belief", bayesian_ci)]:
            cov = 0
            for k in ks:
                lo, hi = fn(int(k), n)
                if lo <= 0.5 <= hi:
                    cov += 1
            rates[name].append(cov / n_trials)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    colors = [PALETTE["focus"], PALETTE["contrast"], PALETTE["support"], "#7a9b76"]
    for (name, vals), color in zip(rates.items(), colors):
        ax.plot(sizes, vals, "o-", color=color, linewidth=1.8, markersize=7, label=name)
    ax.axhline(0.95, color=PALETTE["muted"], linestyle="--", linewidth=1, label="promised 95%")
    ax.set_xscale("log")
    ax.set_xlabel("number of tosses (log scale)")
    ax.set_ylabel("fraction of intervals that contained the true bias 0.5")
    ax.set_ylim(0.6, 1.02)
    ax.legend(loc="lower right")
    ax.set_title("at true bias 0.5, how often does each procedure deliver its 95% promise?")
    out = IMG_DIR / "coverage_at_p_50.png"
    fig.savefig(out)
    plt.close(fig)
    return out, rates


def render_coverage_vs_p():
    """At fixed N, coverage as the true p varies. Wald wiggles."""
    apply_story_style()
    rng = np.random.default_rng(456)
    n = 30
    n_trials = 3000
    ps = np.linspace(0.02, 0.98, 49)
    rates = {name: [] for name in ["Wald", "Wilson", "Clopper-Pearson", "Belief"]}
    for p in ps:
        ks = rng.binomial(n, p, size=n_trials)
        for name, fn in [("Wald", wald_ci), ("Wilson", wilson_ci),
                         ("Clopper-Pearson", clopper_pearson_ci), ("Belief", bayesian_ci)]:
            cov = 0
            for k in ks:
                lo, hi = fn(int(k), n)
                if lo <= p <= hi:
                    cov += 1
            rates[name].append(cov / n_trials)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    colors = [PALETTE["focus"], PALETTE["contrast"], PALETTE["support"], "#7a9b76"]
    for (name, vals), color in zip(rates.items(), colors):
        ax.plot(ps, vals, color=color, linewidth=1.6, label=name, alpha=0.85)
    ax.axhline(0.95, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_xlabel("true bias p")
    ax.set_ylabel("fraction of 95% intervals that actually contained p")
    ax.set_ylim(0.6, 1.02)
    ax.set_xlim(0, 1)
    ax.legend(loc="lower center")
    ax.set_title(f"with {n} tosses, where Wald breaks down across the bias range")
    out = IMG_DIR / "coverage_vs_p.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_priors_argue():
    """60 heads in 100 tosses through three different priors."""
    apply_story_style()
    ps = np.linspace(0, 1, 1000)
    priors = [(1, 1, "flat (no opinion)", PALETTE["focus"]),
              (50, 50, "skeptical (expect fair)", PALETTE["contrast"]),
              (2, 8, "expects tails", PALETTE["support"])]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.0), sharey=False)
    # Left: priors
    for a, b, label, color in priors:
        axes[0].plot(ps, stats.beta.pdf(ps, a, b), color=color, linewidth=2, label=label)
    axes[0].axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[0].set_xlim(0, 1)
    axes[0].set_xlabel("possible bias")
    axes[0].set_ylabel("how strongly I believed each value before tossing")
    axes[0].set_title("three different starting beliefs (priors)")
    axes[0].legend()
    # Right: posteriors after 60/100
    k, n = 60, 100
    for a, b, label, color in priors:
        post_a, post_b = a + k, b + n - k
        axes[1].plot(ps, stats.beta.pdf(ps, post_a, post_b), color=color, linewidth=2, label=label)
    axes[1].axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[1].set_xlim(0, 1)
    axes[1].set_xlabel("possible bias")
    axes[1].set_ylabel("how strongly I believe each value after seeing 60/100")
    axes[1].set_title("same data, three different ending beliefs")
    axes[1].legend()
    out = IMG_DIR / "priors_argue.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    paths = []
    paths.append((render_intervals_at_observations(), "derived",
                  "Story Ch.5: four 95% interval procedures applied to 6/10, 60/100, 600/1000"))
    paths.append((render_boundary_failures(), "derived",
                  "Story Ch.5: 0/10, 10/10, 1/100, 99/100 - where Wald collapses"))
    p_cov, rates = render_coverage_at_p_50()
    paths.append((p_cov, 123,
                  f"Story Ch.5: coverage at p=0.5 across N (5/10/20/50/100), 5000 trials each"))
    paths.append((render_coverage_vs_p(), 456,
                  "Story Ch.5: coverage vs true p at N=30, 3000 trials each, showing Wald wiggle"))
    paths.append((render_priors_argue(), "derived",
                  "Story Ch.5: priors argue, posteriors after 60/100"))
    print(f"Story Ch.5: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
