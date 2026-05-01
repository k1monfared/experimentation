"""Regenerate Chapter 13 (metric tree) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy.stats import spearmanr

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file, save_samples  # noqa: E402
from expkit.metrics.quality import predictivity, signal_to_noise  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402

CHAPTER = "13-metric-tree"
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


def render_tree_diagram():
    apply_style()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis("off")
    layers = [
        (4.5, "company outcome\n(retention, revenue)"),
        (3.0, "first-layer proxies\n(DAU, conversion, churn)"),
        (1.5, "session-level\n(sessions/week, time/session)"),
        (0.0, "click-level\n(CTR, scroll depth, dwell)"),
    ]
    cmap = plt.get_cmap("viridis")
    for i, (y, text) in enumerate(layers):
        ax.add_patch(plt.Rectangle((1, y), 8, 1.0, color=cmap(i / max(1, len(layers) - 1)), alpha=0.65))
        ax.text(5, y + 0.5, text, ha="center", va="center", fontsize=11)
    for i in range(len(layers) - 1):
        ax.annotate("", xy=(5, layers[i][0]), xytext=(5, layers[i + 1][0] + 1.0), arrowprops=dict(arrowstyle="->"))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 6)
    ax.set_title("Loop A: the metric tree -- truth at the top, signal at the bottom")
    fig.tight_layout()
    out = IMG_DIR / "metric_tree.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_noise_vs_speed():
    apply_style()
    layers = ["click", "session", "first-layer\nproxy", "company\noutcome"]
    relative_noise_per_layer = [0.04, 0.10, 0.30, 1.20]
    measurement_speed = [1, 7, 30, 180]  # days needed to read it reliably
    fig, ax = plt.subplots()
    ax.scatter(measurement_speed, relative_noise_per_layer, s=120, color=plt.get_cmap("viridis")(np.linspace(0, 1, len(layers))))
    for x, y, l in zip(measurement_speed, relative_noise_per_layer, layers):
        ax.annotate(l, (x, y), xytext=(8, 6), textcoords="offset points")
    ax.set_xlabel("days needed for a reliable read (log)")
    ax.set_ylabel("relative noise (CV) per measurement -- illustrative")
    ax.set_xscale("log")
    ax.set_title("Schematic: lower-level metrics tend to be faster and cleaner")
    # Caption: numbers are illustrative, not measured. Real values vary by product.
    fig.text(
        0.5,
        -0.02,
        "Numbers are illustrative, not measured. Real values vary by product.",
        ha="center",
        va="top",
        fontsize=9,
        style="italic",
    )
    fig.tight_layout()
    out = IMG_DIR / "noise_vs_speed.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def render_predictivity_simulation(manifest):
    """Simulate 200 experiments. For each, record a short-term metric effect (CTR) and a long-term metric effect (retention)."""
    apply_style()
    rng = np.random.default_rng(0)
    n = 200
    truths = rng.normal(0, 0.02, size=n)  # true latent effect
    # Short-term metric: very correlated but very noisy
    short_term = truths * 0.6 + rng.normal(0, 0.03, size=n)
    # Long-term metric: less noisy, less correlated with truth on its own
    long_term = truths * 0.9 + rng.normal(0, 0.01, size=n)
    save_samples(np.column_stack([short_term, long_term]), DATA_DIR / "predictivity_pairs", seed=0, meta={"n": n})

    # Pearson r with bootstrap 95% CI, plus Spearman rho.
    pred = predictivity(short_term, long_term, n_boot=1000, seed=0)
    rho, _ = spearmanr(short_term, long_term)

    # Save bootstrap distribution of r so the CI is reproducible.
    rng_b = np.random.default_rng(0)
    rs = np.empty(1000, dtype=float)
    for i in range(1000):
        idx = rng_b.integers(0, n, size=n)
        c = np.cov(short_term[idx], long_term[idx], ddof=1)
        rs[i] = c[0, 1] / np.sqrt(c[0, 0] * c[1, 1])
    save_samples(rs, DATA_DIR / "predictivity_bootstrap_r", seed=0, meta={"n_boot": 1000, "stat": "pearson_r"})

    fig, ax = plt.subplots()
    ax.scatter(short_term, long_term, alpha=0.5, color=PALETTE["frequentist"])
    # Linear fit
    coef = np.polyfit(short_term, long_term, 1)
    xs = np.array([short_term.min(), short_term.max()])
    label = (
        f"fit: Pearson r = {pred['pearson_r']:.2f} "
        f"[{pred['ci_95_low']:.2f}, {pred['ci_95_high']:.2f}], "
        f"Spearman rho = {rho:.2f}, R^2 = {pred['r_squared']:.2f}"
    )
    ax.plot(xs, np.polyval(coef, xs), color=PALETTE["bayesian"], label=label)
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_xlabel("short-term metric (CTR) effect per experiment")
    ax.set_ylabel("long-term metric (retention) effect per experiment")
    ax.set_title("Loop C: predictivity -- when does short-term anticipate long-term?")
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    out = IMG_DIR / "predictivity.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_proxy_lies():
    """Three different proxies. Two correlate with outcome; one is anticorrelated.

    Real-world anchor for the lying proxy: clicks vs revenue can anti-correlate
    when bounce rate dominates. A clickbait variant pulls clicks but burns
    brand and reduces revenue. Chapter 16 examines the mechanism.
    """
    apply_style()
    rng = np.random.default_rng(1)
    n = 150
    truth = rng.normal(0, 0.02, n)
    a = truth + rng.normal(0, 0.02, n)
    b = truth + rng.normal(0, 0.04, n)
    c = -0.5 * truth + rng.normal(0, 0.03, n)  # this proxy lies
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6), sharey=True)
    for ax, x, t in zip(axes, [a, b, c], ["good proxy A", "noisy proxy B", "lying proxy C"]):
        r = float(np.corrcoef(x, truth)[0, 1])
        ax.scatter(x, truth, alpha=0.5)
        ax.set_xlabel(f"{t} (r = {r:+.2f})")
        ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[0].set_ylabel("true effect")
    fig.suptitle("Loop D: three candidate proxies. Two predict the truth, one is anti-correlated.")
    fig.text(
        0.5,
        -0.02,
        "Real anchor: clicks vs revenue can anti-correlate when bounce-rate dominates "
        "(clickbait pulls clicks but burns brand). Chapter 16 examines the mechanism.",
        ha="center",
        va="top",
        fontsize=9,
        style="italic",
    )
    fig.tight_layout()
    out = IMG_DIR / "proxy_lies.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_tree_diagram(),
        render_noise_vs_speed(),
        render_predictivity_simulation(manifest),
        render_proxy_lies(),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 13 figure: {p.name}")
    samples = DATA_DIR / "predictivity_pairs.npy"
    if samples.exists():
        add_artifact(manifest, path=samples, kind="samples", seed=0, sha256=_sha256_file(samples), description="Loop C: short-term vs long-term effect pairs across 200 simulated experiments")
    boot = DATA_DIR / "predictivity_bootstrap_r.npy"
    if boot.exists():
        add_artifact(manifest, path=boot, kind="samples", seed=0, sha256=_sha256_file(boot), description="Loop C: bootstrap distribution of Pearson r (1000 resamples)")
    save_manifest(manifest)
    print(f"Chapter 13: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
