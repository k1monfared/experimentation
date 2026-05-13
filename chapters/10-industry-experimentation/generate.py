"""Regenerate Chapter 10 (industry experimentation) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402

CHAPTER = "10-industry-experimentation"
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


def render_clickbait_curves():
    """Short-term up, long-term down."""
    apply_style()
    days = np.arange(0, 30)
    rng = np.random.default_rng(0)
    # Treatment: clicks up by 10% on day 1, decays toward 0 by day 30; retention down 5% by day 30
    click_lift = 0.10 * np.exp(-days / 7)
    retention_lift = -0.05 * (1 - np.exp(-days / 14))
    fig, ax = plt.subplots()
    ax.plot(days, 100 * click_lift, color=PALETTE["frequentist"], label="click rate lift (%)")
    ax.plot(days, 100 * retention_lift, color=PALETTE["bayesian"], label="7-day retention lift (%)")
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_xlabel("days since launch")
    ax.set_ylabel("lift over control (%)")
    ax.set_title("Loop B: clickbait -- clicks up, retention down. Both stories are true.")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "clickbait_curves.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_aggregate_hides_structure():
    """Aggregate +4% click rate. Most engaged users -2%, long tail +15%."""
    apply_style()
    segments = ["most engaged 10%", "moderately engaged 30%", "long tail 60%"]
    fractions = [0.10, 0.30, 0.60]
    lifts = [-0.02, 0.03, 0.06]
    aggregate_lift = sum(f * l for f, l in zip(fractions, lifts))
    fig, ax = plt.subplots()
    cmap = plt.get_cmap("viridis")
    bars = ax.bar(segments + ["aggregate"], lifts + [aggregate_lift], color=[cmap(i / 3) for i in range(4)])
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    for b, v in zip(bars, lifts + [aggregate_lift]):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.001, f"{v:+.3f}", ha="center")
    ax.set_ylabel("click-rate lift")
    ax.set_title("Loop C: '+4% on average' hides that the most engaged 10% lost ground")
    fig.tight_layout()
    out = IMG_DIR / "aggregate_hides_structure.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_guardrails_vs_decision():
    """Many guardrail tests one of which is wrong by chance."""
    apply_style()
    rng = np.random.default_rng(0)
    n_metrics = 20
    n_runs = 5000
    # All metrics under H0. Naive: any p<0.05 fires guardrail. Bonferroni: 0.05/20 each.
    naive_fp = 0
    bonf_fp = 0
    for _ in range(n_runs):
        pvals = rng.uniform(0, 1, size=n_metrics)
        if any(p < 0.05 for p in pvals):
            naive_fp += 1
        if any(p < 0.05 / n_metrics for p in pvals):
            bonf_fp += 1
    fig, ax = plt.subplots()
    ax.bar(["naive (each at 0.05)", "Bonferroni (each at 0.05/20)"], [naive_fp / n_runs, bonf_fp / n_runs], color=[PALETTE["frequentist"], PALETTE["bayesian"]])
    ax.axhline(0.05, color=PALETTE["muted"], linestyle="--", linewidth=1)
    for x, v in zip([0, 1], [naive_fp / n_runs, bonf_fp / n_runs]):
        ax.text(x, v + 0.005, f"{v:.3f}", ha="center")
    ax.set_ylabel("family-wise type-I rate")
    ax.set_title(f"Loop D: 20 guardrails, all under H0. Naive false-positives blow up.")
    fig.tight_layout()
    out = IMG_DIR / "guardrails.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_hierarchical_shrinkage():
    """Loop D compare panel: per-metric CIs vs hierarchical shrunk posteriors.

    Simulate 20 guardrail metrics under H0 (all true lifts = 0). Compare
    two readings of the same data: marginal per-metric 95% intervals
    (flat prior, behaves like the naive frequentist check) and a
    hierarchical empirical-Bayes shrinkage posterior that pulls each
    metric toward the population mean using the DerSimonian-Laird
    variance estimator. The shrunk intervals tuck back toward zero and
    the family-wise alarm rate drops without any Bonferroni threshold.
    """
    apply_style()
    rng = np.random.default_rng(0)
    n_metrics = 20
    sigma = 1.0  # per-metric standard error of the lift estimate
    true_lift = np.zeros(n_metrics)
    y = true_lift + sigma * rng.standard_normal(n_metrics)  # observed lift estimates

    # Marginal (flat-prior) 95% CI per metric
    marg_lo = y - 1.96 * sigma
    marg_hi = y + 1.96 * sigma

    # Empirical-Bayes / DerSimonian-Laird shrinkage toward a shared mean
    # weights = 1 / sigma^2; weighted mean; Q statistic; tau^2 estimate
    w = np.full(n_metrics, 1.0 / sigma ** 2)
    mu_hat = np.sum(w * y) / np.sum(w)
    Q = np.sum(w * (y - mu_hat) ** 2)
    df = n_metrics - 1
    c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (Q - df) / c)
    # Posterior mean and variance per metric under Normal-Normal pooling
    shrink_var = 1.0 / (1.0 / sigma ** 2 + 1.0 / tau2) if tau2 > 0 else np.zeros(n_metrics) + 1e-12
    post_mean = shrink_var * (y / sigma ** 2 + mu_hat / tau2) if tau2 > 0 else np.full(n_metrics, mu_hat)
    post_sd = np.sqrt(shrink_var) if tau2 > 0 else np.zeros(n_metrics)
    hier_lo = post_mean - 1.96 * post_sd
    hier_hi = post_mean + 1.96 * post_sd

    fig, ax = plt.subplots(figsize=(8, 5))
    xs = np.arange(n_metrics)
    ax.hlines(xs - 0.15, marg_lo, marg_hi, color=PALETTE["frequentist"], linewidth=2, label="marginal 95% CI (flat prior)")
    ax.plot(y, xs - 0.15, "o", color=PALETTE["frequentist"])
    ax.hlines(xs + 0.15, hier_lo, hier_hi, color=PALETTE["bayesian"], linewidth=2, label="hierarchical shrunk 95%")
    ax.plot(post_mean, xs + 0.15, "s", color=PALETTE["bayesian"])
    ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_yticks(xs)
    ax.set_yticklabels([f"metric {i + 1}" for i in range(n_metrics)])
    ax.set_xlabel("lift estimate and 95% interval")
    ax.set_title("Loop D: hierarchical pooling pulls noisy guardrails back toward zero")
    ax.legend(loc="lower right")
    fig.tight_layout()
    out = IMG_DIR / "hierarchical_shrinkage.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_clickbait_curves(),
        render_aggregate_hides_structure(),
        render_guardrails_vs_decision(),
        render_hierarchical_shrinkage(),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 10 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 10: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
