"""Regenerate Chapter 16 (metric quality) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.metrics.quality import predictivity, stability_aa  # noqa: E402
from expkit.metrics.variance import cuped, variance_reduction_ratio  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402

CHAPTER = "16-metric-quality"
CHAPTER_DIR = Path(__file__).resolve().parent
DATA_DIR = CHAPTER_DIR / "data"
IMG_DIR = CHAPTER_DIR / "images"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.yaml"


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
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
    m["artifacts"].append({"path": rel, "chapter": CHAPTER, "kind": kind, "seed": seed, "sha256": sha256, "description": description})


def render_variance_comparison():
    """Three candidate metrics for the same underlying user value, with different variance."""
    apply_style()
    rng = np.random.default_rng(0)
    n = 2000
    truth = rng.normal(10, 2, n)
    metric_a = truth + rng.normal(0, 1, n)
    metric_b = truth + rng.normal(0, 5, n)
    metric_c = truth + rng.normal(0, 0.3, n)
    fig, ax = plt.subplots()
    ax.hist(metric_a, bins=50, alpha=0.5, color=PALETTE["frequentist"], label=f"A: var={metric_a.var():.2f}")
    ax.hist(metric_b, bins=50, alpha=0.5, color=PALETTE["bayesian"], label=f"B: var={metric_b.var():.2f}")
    ax.hist(metric_c, bins=50, alpha=0.5, color=PALETTE["highlight"], label=f"C: var={metric_c.var():.2f}")
    ax.set_xlabel("metric value")
    ax.set_ylabel("count")
    ax.set_title("Loop A: three candidate metrics. Same truth. Different noise.")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "variance_comparison.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_cuped(manifest):
    """Apply CUPED with a pre-experiment covariate. Show variance reduction."""
    apply_style()
    rng = np.random.default_rng(0)
    n = 4000
    pre = rng.normal(10, 3, n)
    arm = rng.choice([0, 1], size=n)
    treatment_effect = 0.2
    y = 0.7 * pre + arm * treatment_effect + rng.normal(0, 1, n)
    y_adj, theta = cuped(y, pre)
    reduction = variance_reduction_ratio(y, y_adj)
    fig, ax = plt.subplots()
    ax.hist(y, bins=60, alpha=0.5, color=PALETTE["frequentist"], label=f"raw y (var={y.var():.2f})")
    ax.hist(y_adj, bins=60, alpha=0.5, color=PALETTE["bayesian"], label=f"CUPED-adjusted (var={y_adj.var():.2f}, theta={theta:.2f})")
    ax.set_xlabel("y")
    ax.set_ylabel("count")
    ax.set_title(f"Loop B: CUPED reduces variance by {100*reduction:.0f}% on these data")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "cuped.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_aa_stability():
    """Run an A/A test many times. Empirical false positive rate should match alpha."""
    apply_style()
    rng = np.random.default_rng(0)
    n_per_arm = 500
    n_trials = 5000
    effects = []
    for _ in range(n_trials):
        c = rng.normal(0, 1, n_per_arm)
        t = rng.normal(0, 1, n_per_arm)
        effects.append(t.mean() - c.mean())
    s = stability_aa(np.array(effects))
    fig, ax = plt.subplots()
    ax.hist(effects, bins=50, color=PALETTE["frequentist"], alpha=0.7)
    ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_xlabel("measured effect (treatment - control)")
    ax.set_ylabel(f"count over {n_trials} A/A tests")
    ax.set_title(f"Loop C: A/A test distribution. mean = {s['mean']:+.4f}, frac |effect| > 1.96 std = {s['frac_extreme']:.3f}")
    fig.tight_layout()
    out = IMG_DIR / "aa_stability.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_predictivity_grid(manifest):
    """For 200 simulated experiments, plot short-term and long-term effects, with predictivity scorer."""
    apply_style()
    rng = np.random.default_rng(7)
    n = 200
    truth = rng.normal(0, 0.02, size=n)
    short_a = truth * 0.8 + rng.normal(0, 0.02, n)  # good predictor
    short_b = truth * 0.0 + rng.normal(0, 0.04, n)  # noise
    short_c = -truth * 0.4 + rng.normal(0, 0.02, n)  # liar
    long_term = truth * 0.95 + rng.normal(0, 0.005, n)
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6), sharey=True)
    for ax, x, label in zip(axes, [short_a, short_b, short_c], ["good A", "noise B", "liar C"]):
        pred = predictivity(x, long_term)
        ax.scatter(x, long_term, alpha=0.5)
        ax.set_xlabel(f"short-term {label} (r={pred['pearson_r']:+.2f})")
        ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[0].set_ylabel("long-term metric")
    fig.suptitle("Loop D: predictivity score lets us pick metrics worth optimizing")
    fig.tight_layout()
    out = IMG_DIR / "predictivity_grid.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_variance_comparison(),
        render_cuped(manifest),
        render_aa_stability(),
        render_predictivity_grid(manifest),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 16 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 16: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
