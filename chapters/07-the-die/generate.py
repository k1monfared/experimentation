"""Regenerate Chapter 7 (the six-sided die) figures and data."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy.stats import dirichlet

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.inference.chi2 import goodness_of_fit  # noqa: E402
from expkit.io.samples import _sha256_file, save_samples  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.sim.die import (  # noqa: E402
    dirichlet_posterior_mean,
    face_counts,
    fair_die_rolls,
    loaded_die_rolls,
)

CHAPTER = "07-the-die"
CHAPTER_DIR = Path(__file__).resolve().parent
DATA_DIR = CHAPTER_DIR / "data"
IMG_DIR = CHAPTER_DIR / "images"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.yaml"

SEEDS = {"fair": 70, "loaded": 71, "monte_carlo": 72}


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


def render_count_wobble():
    apply_style()
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6), sharey=True)
    for ax, n in zip(axes, [60, 600, 6000]):
        rolls = fair_die_rolls(n, seed=SEEDS["fair"] + n)
        counts = face_counts(rolls)
        ax.bar(np.arange(1, 7), counts, color=PALETTE["frequentist"], alpha=0.85)
        ax.axhline(n / 6, color=PALETTE["muted"], linestyle="--", linewidth=1, label=f"expected if fair = {n/6:.1f}")
        ax.set_xlabel("face")
        ax.set_title(f"N = {n}")
        ax.legend(fontsize=8)
    axes[0].set_ylabel("count")
    fig.suptitle("Loop A: face counts wobble around the expected value")
    fig.tight_layout()
    out = IMG_DIR / "count_wobble.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_chi2_pvalue_curve(manifest):
    """Run a goodness-of-fit test on a fair die and a loaded one (p_6 = 1/3)."""
    apply_style()
    loaded_p = np.array([2 / 15, 2 / 15, 2 / 15, 2 / 15, 2 / 15, 1 / 3])
    ns = np.unique(np.round(np.geomspace(30, 6000, 60)).astype(int))
    fig, ax = plt.subplots()
    rng = np.random.default_rng(SEEDS["monte_carlo"])
    fair_pvals = []
    loaded_pvals = []
    for n in ns:
        fair = fair_die_rolls(int(n), seed=int(rng.integers(0, 2**30)))
        loaded = loaded_die_rolls(int(n), p=loaded_p, seed=int(rng.integers(0, 2**30)))
        f_res = goodness_of_fit(face_counts(fair), expected_p=np.ones(6) / 6)
        l_res = goodness_of_fit(face_counts(loaded), expected_p=np.ones(6) / 6)
        fair_pvals.append(f_res.p_value)
        loaded_pvals.append(l_res.p_value)
    save_samples(np.array([fair_pvals, loaded_pvals]).T, DATA_DIR / "chi2_pvalues_grid", seed=SEEDS["monte_carlo"], meta={"ns": ns.tolist(), "loaded_p": loaded_p.tolist()})
    ax.plot(ns, fair_pvals, color=PALETTE["frequentist"], label="fair die")
    ax.plot(ns, loaded_pvals, color=PALETTE["bayesian"], label="loaded (p_6 = 1/3)")
    ax.axhline(0.05, color=PALETTE["muted"], linestyle="--", linewidth=1, label="alpha = 0.05")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("N (log scale)")
    ax.set_ylabel("chi-square goodness-of-fit p-value")
    ax.set_title("Loop B: chi-square detects loading -- but only at sufficient N")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "chi2_pvalues.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_dirichlet_posterior():
    apply_style()
    n = 600
    loaded_p = np.array([2 / 15, 2 / 15, 2 / 15, 2 / 15, 2 / 15, 1 / 3])
    rolls = loaded_die_rolls(n, p=loaded_p, seed=SEEDS["loaded"])
    counts = face_counts(rolls)

    rng = np.random.default_rng(0)
    posterior_alpha = np.ones(6) + counts
    draws = rng.dirichlet(posterior_alpha, size=20000)

    fig, ax = plt.subplots()
    cmap = plt.get_cmap("viridis")
    for face_idx in range(6):
        ax.hist(draws[:, face_idx], bins=80, density=True, alpha=0.5, color=cmap(face_idx / 5), label=f"face {face_idx+1}")
    ax.axvline(1 / 6, color=PALETTE["muted"], linestyle="--", linewidth=1, label="fair = 1/6")
    ax.axvline(1 / 3, color=PALETTE["highlight"], linestyle=":", linewidth=1, label="true face-6 prob = 1/3")
    ax.set_xlabel("posterior probability of each face")
    ax.set_ylabel("posterior density")
    ax.set_title(f"Loop C: Dirichlet-multinomial posterior on each face (N = {n})")
    ax.legend(ncols=2, fontsize=8)
    fig.tight_layout()
    out = IMG_DIR / "dirichlet_posterior.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_multiple_comparisons():
    """Single-test alpha vs family-wise error rate when testing each face individually."""
    apply_style()
    n = 600
    n_trials = 1000
    rng = np.random.default_rng(SEEDS["monte_carlo"])
    fwer_naive = 0
    fwer_bonferroni = 0
    individual_alpha = 0.05
    bonf_alpha = individual_alpha / 6

    from expkit.inference.binomial import binom_test_exact
    for _ in range(n_trials):
        rolls = fair_die_rolls(n, seed=int(rng.integers(0, 2**30)))
        counts = face_counts(rolls)
        rejected_naive = False
        rejected_bonf = False
        for face_idx, k in enumerate(counts):
            pval = binom_test_exact(int(k), n, p_null=1 / 6).p_value
            if pval < individual_alpha:
                rejected_naive = True
            if pval < bonf_alpha:
                rejected_bonf = True
        if rejected_naive:
            fwer_naive += 1
        if rejected_bonf:
            fwer_bonferroni += 1
    fwer_naive /= n_trials
    fwer_bonferroni /= n_trials

    fig, ax = plt.subplots()
    ax.bar(["naive (each face at 0.05)", "Bonferroni (each face at 0.05/6)"], [fwer_naive, fwer_bonferroni], color=[PALETTE["frequentist"], PALETTE["bayesian"]])
    for x, v in zip([0, 1], [fwer_naive, fwer_bonferroni]):
        ax.text(x, v + 0.005, f"{v:.3f}", ha="center")
    ax.axhline(0.05, color=PALETTE["muted"], linestyle="--", linewidth=1, label="nominal 0.05")
    ax.set_ylabel("family-wise type-I rate")
    ax.set_title(f"Loop D: testing each face individually (N = {n}, {n_trials} fair-die simulations)")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "multiple_comparisons.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_count_wobble(),
        render_chi2_pvalue_curve(manifest),
        render_dirichlet_posterior(),
        render_multiple_comparisons(),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 7 figure: {p.name}")
    samples = DATA_DIR / "chi2_pvalues_grid.npy"
    if samples.exists():
        add_artifact(manifest, path=samples, kind="samples", seed=SEEDS["monte_carlo"], sha256=_sha256_file(samples), description="Loop B: chi-square p-values for fair vs loaded die at varying N")
    save_manifest(manifest)
    print(f"Chapter 7: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
