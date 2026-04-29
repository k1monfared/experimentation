"""Regenerate Chapter 2 datasets and figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.inference.bayes import coin_posterior_conjugate  # noqa: E402
from expkit.inference.binomial import binom_test_exact  # noqa: E402
from expkit.io.samples import _sha256_file, save_samples  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.power.binomial import simulate_rejection_rate  # noqa: E402
from expkit.sim.coin import bernoulli_sequence  # noqa: E402

CHAPTER = "02-how-sure"
CHAPTER_DIR = Path(__file__).resolve().parent
DATA_DIR = CHAPTER_DIR / "data"
IMG_DIR = CHAPTER_DIR / "images"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.yaml"

SEEDS = {"sampling_dist": 100, "rejection_rates": 200}


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return yaml.safe_load(MANIFEST_PATH.read_text()) or {"artifacts": []}
    return {"artifacts": []}


def save_manifest(m: dict) -> None:
    MANIFEST_PATH.write_text(yaml.safe_dump(m, sort_keys=False))


def add_artifact(m, *, path, kind, seed, sha256, description):
    rel = str(path.relative_to(REPO_ROOT))
    m["artifacts"] = [a for a in m["artifacts"] if a.get("path") != rel]
    m["artifacts"].append(
        {"path": rel, "chapter": CHAPTER, "kind": kind, "seed": seed, "sha256": sha256, "description": description}
    )


def render_sampling_distribution() -> Path:
    """Distribution of head counts in 100 tosses of a fair coin, with rejection region."""
    apply_style()
    n = 100
    p_null = 0.5
    counts = np.arange(0, n + 1)
    pmf = stats.binom.pmf(counts, n, p_null)
    pvals = np.array([stats.binomtest(int(k), n, p=p_null).pvalue for k in counts])
    reject = pvals < 0.05

    fig, ax = plt.subplots()
    bar_colors = [PALETTE["highlight"] if r else PALETTE["frequentist"] for r in reject]
    ax.bar(counts, pmf, color=bar_colors, alpha=0.85, width=0.9)
    ax.axvline(50, color=PALETTE["muted"], linestyle="--", linewidth=1, label="expected if fair (50)")
    ax.set_xlabel("heads in 100 tosses")
    ax.set_ylabel("probability under H0")
    ax.set_title("Loop A: sampling distribution under a fair coin (rejection region in green)")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "sampling_distribution_n100.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_decision_curves(manifest: dict) -> tuple[Path, np.ndarray]:
    """Both lenses agreeing/disagreeing as a function of observed heads in 10 and 100 tosses."""
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, n in zip(axes, [10, 100]):
        ks = np.arange(0, n + 1)
        pvals = np.array([stats.binomtest(int(k), n, p=0.5).pvalue for k in ks])
        post_probs = np.array(
            [coin_posterior_conjugate(np.array([1] * int(k) + [0] * (n - int(k)))).prob_greater_than(0.5) for k in ks]
        )
        ax.plot(ks, pvals, color=PALETTE["frequentist"], label="frequentist p-value")
        ax.plot(ks, post_probs, color=PALETTE["bayesian"], label="Bayesian P(p > 0.5)")
        ax.axhline(0.05, color=PALETTE["muted"], linestyle="--", linewidth=1, label="alpha = 0.05")
        ax.axhline(0.95, color=PALETTE["muted"], linestyle=":", linewidth=1, label="P(p>0.5) = 0.95")
        ax.set_xlabel(f"heads observed (out of {n})")
        ax.set_title(f"N = {n}")
        ax.legend(loc="best", fontsize=8)
    axes[0].set_ylabel("decision quantity")
    fig.suptitle("Loop B: each lens at every possible observation")
    fig.tight_layout()
    out = IMG_DIR / "decision_curves.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_alpha_sweep() -> Path:
    """How the rejection region grows/shrinks with alpha."""
    apply_style()
    n = 100
    counts = np.arange(0, n + 1)
    pmf = stats.binom.pmf(counts, n, 0.5)
    pvals = np.array([stats.binomtest(int(k), n, p=0.5).pvalue for k in counts])
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.0))
    for ax, alpha in zip(axes, [0.1, 0.05, 0.01]):
        reject = pvals < alpha
        bar_colors = [PALETTE["highlight"] if r else PALETTE["frequentist"] for r in reject]
        ax.bar(counts, pmf, color=bar_colors, alpha=0.85, width=0.9)
        ax.set_title(f"alpha = {alpha:.2f}")
        ax.set_xlabel("heads in 100 tosses")
        ax.set_xlim(20, 80)
    axes[0].set_ylabel("probability under H0")
    fig.suptitle("Loop C: the rejection region grows or shrinks with alpha")
    fig.tight_layout()
    out = IMG_DIR / "alpha_sweep.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_simulated_decisions(manifest: dict) -> Path:
    """Empirical false-positive and true-positive rates across 5,000 sim-experiments per scenario."""
    apply_style()
    truths = [0.50, 0.52, 0.55, 0.60]
    ns = [50, 200, 1000]
    rates = np.zeros((len(truths), len(ns)))
    for i, p in enumerate(truths):
        for j, n in enumerate(ns):
            rates[i, j] = simulate_rejection_rate(p, n, p_null=0.5, alpha=0.05, n_experiments=2000, seed=SEEDS["rejection_rates"] + j)
    save_samples(rates, DATA_DIR / "rejection_rates_grid", seed=SEEDS["rejection_rates"], meta={"truths": truths, "ns": ns, "n_experiments": 2000})

    fig, ax = plt.subplots()
    width = 0.22
    xs = np.arange(len(truths))
    for j, n in enumerate(ns):
        offsets = (j - 1) * width
        ax.bar(xs + offsets, rates[:, j], width=width, label=f"N = {n}")
    ax.set_xticks(xs)
    ax.set_xticklabels([f"p = {p:.2f}" for p in truths])
    ax.set_ylabel("rejection rate")
    ax.set_ylim(0, 1.05)
    ax.axhline(0.05, color=PALETTE["muted"], linestyle="--", linewidth=1, label="alpha = 0.05")
    ax.set_title("Loop D: empirical rejection rate vs true coin bias")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "rejection_rates.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main() -> None:
    ensure_dirs()
    manifest = load_manifest()

    paths = [
        render_sampling_distribution(),
        render_decision_curves(manifest),
        render_alpha_sweep(),
        render_simulated_decisions(manifest),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 2 figure: {p.name}")
    # The samples file is already added by save_samples; record its sidecar entry.
    samples_path = DATA_DIR / "rejection_rates_grid.npy"
    if samples_path.exists():
        add_artifact(manifest, path=samples_path, kind="samples", seed=SEEDS["rejection_rates"], sha256=_sha256_file(samples_path),
                     description="Loop D: empirical rejection rates across (truth, N) grid")

    save_manifest(manifest)
    print(f"Chapter 2: wrote {len(paths)} figures + 1 samples grid")


if __name__ == "__main__":
    main()
