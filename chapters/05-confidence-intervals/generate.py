"""Regenerate Chapter 5 (confidence intervals) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy.stats import beta as beta_dist
from statsmodels.stats.proportion import proportion_confint

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.inference.binomial import clopper_pearson_ci, wilson_ci  # noqa: E402
from expkit.inference.bootstrap import bootstrap_ci  # noqa: E402
from expkit.io.samples import _sha256_file, save_samples  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.sim.coin import bernoulli_sequence  # noqa: E402

CHAPTER = "05-confidence-intervals"
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


def render_method_comparison():
    """Wald, Wilson, Clopper-Pearson, bootstrap, Bayesian credible at three sample sizes."""
    apply_style()
    cases = [(6, 10), (60, 100), (600, 1000)]
    methods = ["Wald", "Wilson", "Clopper-Pearson", "Bootstrap", "Bayesian (Beta(1,1))"]
    fig, axes = plt.subplots(1, len(cases), figsize=(13, 3.8), sharey=True)
    for ax, (k, n) in zip(axes, cases):
        intervals = []
        wald_lo, wald_hi = proportion_confint(k, n, alpha=0.05, method="normal")
        intervals.append(("Wald", wald_lo, wald_hi))
        w_lo, w_hi = wilson_ci(k, n)
        intervals.append(("Wilson", w_lo, w_hi))
        cp_lo, cp_hi = clopper_pearson_ci(k, n)
        intervals.append(("Clopper-Pearson", cp_lo, cp_hi))
        seq = np.concatenate([np.ones(k), np.zeros(n - k)])
        bs_lo, bs_hi, _ = bootstrap_ci(seq, n_boot=4000, alpha=0.05, seed=42)
        intervals.append(("Bootstrap", bs_lo, bs_hi))
        a, b = 1 + k, 1 + (n - k)
        b_lo, b_hi = float(beta_dist.ppf(0.025, a, b)), float(beta_dist.ppf(0.975, a, b))
        intervals.append(("Bayesian (Beta(1,1))", b_lo, b_hi))

        ys = np.arange(len(intervals))
        cmap = plt.get_cmap("viridis")
        for j, (name, lo, hi) in enumerate(intervals):
            ax.errorbar((lo + hi) / 2, ys[j], xerr=[[(lo + hi) / 2 - lo], [hi - (lo + hi) / 2]], fmt="o", color=cmap(j / max(1, len(intervals) - 1)), capsize=4)
        ax.axvline(k / n, color=PALETTE["muted"], linestyle="--", linewidth=1, label=f"point estimate {k/n:.2f}")
        ax.set_yticks(ys)
        ax.set_yticklabels([name for name, _, _ in intervals])
        ax.set_xlabel("p")
        ax.set_xlim(0, 1)
        ax.set_title(f"{k}/{n}")
        ax.legend(loc="lower right", fontsize=8)
    fig.suptitle("Loop A: five 95% intervals on the same data, three sample sizes")
    fig.tight_layout()
    out = IMG_DIR / "ci_method_comparison.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_boundary_failures():
    """At extreme observations the methods diverge sharply."""
    apply_style()
    extreme_cases = [(0, 10), (10, 10), (0, 100), (100, 100)]
    rows = []
    for k, n in extreme_cases:
        wald_lo, wald_hi = proportion_confint(k, n, alpha=0.05, method="normal")
        w_lo, w_hi = wilson_ci(k, n)
        cp_lo, cp_hi = clopper_pearson_ci(k, n)
        a, b = 1 + k, 1 + (n - k)
        b_lo = float(beta_dist.ppf(0.025, a, b))
        b_hi = float(beta_dist.ppf(0.975, a, b))
        rows.append((k, n, wald_lo, wald_hi, w_lo, w_hi, cp_lo, cp_hi, b_lo, b_hi))

    fig, ax = plt.subplots(figsize=(11, 4.0))
    ax.axis("off")
    lines = [f"{'k/n':>6}  {'Wald':>16}  {'Wilson':>16}  {'Clopper-Pearson':>22}  {'Bayesian':>16}"]
    for k, n, wl, wh, w_lo, w_hi, cl, ch, bl, bh in rows:
        lines.append(f"{k:>3}/{n:<3}  [{wl:.3f}, {wh:.3f}]  [{w_lo:.3f}, {w_hi:.3f}]  [{cl:.3f}, {ch:.3f}]      [{bl:.3f}, {bh:.3f}]")
    ax.text(0.0, 0.95, "\n".join(lines), family="monospace", fontsize=10, va="top")
    ax.set_title("Loop B: edge cases. Wald collapses to [0,0] or [1,1] -- meaningless. Others stay sane.")
    fig.tight_layout()
    out = IMG_DIR / "boundary_failures.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_three_priors():
    """Same 60/100 data, three priors."""
    apply_style()
    k, n = 60, 100
    priors = [("Beta(1, 1) flat", 1.0, 1.0), ("Beta(50, 50) skeptical", 50.0, 50.0), ("Beta(2, 8) expects-tails", 2.0, 8.0)]
    fig, ax = plt.subplots()
    ps = np.linspace(0, 1, 1000)
    cmap = plt.get_cmap("viridis")
    for j, (name, a0, b0) in enumerate(priors):
        post_a, post_b = a0 + k, b0 + (n - k)
        ax.plot(ps, beta_dist.pdf(ps, post_a, post_b), color=cmap(j / max(1, len(priors) - 1)), label=f"{name} -> Beta({post_a:.0f}, {post_b:.0f})")
    ax.axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.axvline(k / n, color=PALETTE["highlight"], linestyle=":", linewidth=1, label=f"point estimate {k/n:.2f}")
    ax.set_xlabel("p")
    ax.set_ylabel("posterior density")
    ax.set_title("Loop C: 60/100 viewed under three priors")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "three_priors.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_coverage_simulation(manifest):
    """Simulate 5,000 fair-coin experiments at N=20 and check empirical coverage."""
    apply_style()
    n = 20
    n_trials = 5000
    rng = np.random.default_rng(123)
    counts = rng.binomial(n, 0.5, size=n_trials)
    methods = {"Wald": "normal", "Wilson": "wilson", "Clopper-Pearson": "beta"}
    coverage = {name: 0 for name in methods}
    coverage["Bayesian"] = 0
    for k in counts:
        for name, m in methods.items():
            lo, hi = proportion_confint(int(k), n, alpha=0.05, method=m)
            if lo <= 0.5 <= hi:
                coverage[name] += 1
        # Bayesian credible interval
        a, b = 1 + int(k), 1 + (n - int(k))
        lo = float(beta_dist.ppf(0.025, a, b))
        hi = float(beta_dist.ppf(0.975, a, b))
        if lo <= 0.5 <= hi:
            coverage["Bayesian"] += 1

    rates = {name: coverage[name] / n_trials for name in coverage}
    save_samples(np.array(list(rates.values())), DATA_DIR / "coverage_rates", seed=123, meta={"n": n, "n_trials": n_trials, "methods": list(rates)})

    fig, ax = plt.subplots()
    names = list(rates)
    vals = list(rates.values())
    cmap = plt.get_cmap("viridis")
    bars = ax.bar(names, vals, color=[cmap(i / max(1, len(names) - 1)) for i in range(len(names))])
    ax.axhline(0.95, color=PALETTE["muted"], linestyle="--", linewidth=1, label="nominal 95% coverage")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.005, f"{v:.3f}", ha="center")
    ax.set_ylabel("empirical coverage of true p = 0.5")
    ax.set_ylim(0.85, 1.02)
    ax.set_title(f"Loop D: empirical coverage at N = {n} ({n_trials} simulated experiments)")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "coverage_simulation.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_method_comparison(),
        render_boundary_failures(),
        render_three_priors(),
        render_coverage_simulation(manifest),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 5 figure: {p.name}")
    samples_path = DATA_DIR / "coverage_rates.npy"
    if samples_path.exists():
        add_artifact(manifest, path=samples_path, kind="samples", seed=123, sha256=_sha256_file(samples_path), description="Loop D: empirical coverage rates")
    save_manifest(manifest)
    print(f"Chapter 5: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
