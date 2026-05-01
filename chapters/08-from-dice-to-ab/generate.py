"""Regenerate Chapter 8 (from dice to A/B tests) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy.stats import beta as beta_dist

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.inference.bayes import two_arm_posterior  # noqa: E402
from expkit.inference.bootstrap import bootstrap_diff_ci  # noqa: E402
from expkit.inference.normal import two_proportion_z, two_sample_t  # noqa: E402
from expkit.io.samples import _sha256_file, save_idata, save_samples  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.sim.abtest import (  # noqa: E402
    stratified_binary,
    two_arm_binary,
    two_arm_continuous,
)

CHAPTER = "08-from-dice-to-ab"
CHAPTER_DIR = Path(__file__).resolve().parent
DATA_DIR = CHAPTER_DIR / "data"
IMG_DIR = CHAPTER_DIR / "images"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.yaml"

SEEDS = {"binary_small": 80, "binary_large": 81, "continuous": 82, "stratified": 83, "pymc": 808}


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


def render_two_arm_binary():
    apply_style()
    cases = [
        ("hard to detect (1pp lift, N=1000)", 1000, 0.05, 0.06, SEEDS["binary_small"]),
        ("easy to detect (1pp lift, N=10000)", 10000, 0.05, 0.06, SEEDS["binary_large"]),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0))
    for ax, (title, n, pc, pt, sd) in zip(axes, cases):
        exp = two_arm_binary(n, pc, pt, seed=sd)
        z = two_proportion_z(int(exp.treatment.sum()), n, int(exp.control.sum()), n)
        # Bayesian posterior on the difference
        a_c, b_c = 1 + int(exp.control.sum()), 1 + (n - int(exp.control.sum()))
        a_t, b_t = 1 + int(exp.treatment.sum()), 1 + (n - int(exp.treatment.sum()))
        rng = np.random.default_rng(0)
        diffs = rng.beta(a_t, b_t, 5000) - rng.beta(a_c, b_c, 5000)
        ax.hist(diffs, bins=50, density=True, color=PALETTE["bayesian"], alpha=0.6, label="posterior on (treatment - control)")
        ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.axvline(pt - pc, color=PALETTE["highlight"], linestyle=":", linewidth=1, label=f"true effect = {pt-pc:.3f}")
        ax.set_xlabel("treatment minus control")
        ax.set_title(f"{title}\nz = {z.statistic:.2f}, p = {z.p_value:.4g}, P(diff > 0) = {(diffs > 0).mean():.3f}")
        ax.legend(fontsize=8)
    fig.suptitle("Loop A and B: same effect (1pp), small N hides it, large N catches it")
    fig.tight_layout()
    out = IMG_DIR / "two_arm_binary.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_continuous_outcome():
    apply_style()
    exp = two_arm_continuous(2000, mu_control=10.0, mu_treatment=10.5, sigma=4.0, seed=SEEDS["continuous"])
    t = two_sample_t(exp.treatment, exp.control, equal_var=False)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0))
    # Distributions
    axes[0].hist(exp.control, bins=50, density=True, alpha=0.55, color=PALETTE["frequentist"], label="control")
    axes[0].hist(exp.treatment, bins=50, density=True, alpha=0.55, color=PALETTE["bayesian"], label="treatment")
    axes[0].set_xlabel("revenue per user")
    axes[0].set_ylabel("density")
    axes[0].set_title(f"Welch t: t = {t.statistic:.2f}, p = {t.p_value:.4g}")
    axes[0].legend()
    # Bootstrap of the mean difference (uses expkit.inference.bootstrap)
    _lo, _hi, boot_diffs = bootstrap_diff_ci(exp.treatment, exp.control, n_boot=4000, seed=0)
    axes[1].hist(boot_diffs, bins=60, density=True, color=PALETTE["bayesian"], alpha=0.6, label="bootstrap of (treatment - control) mean")
    axes[1].axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[1].axvline(0.5, color=PALETTE["highlight"], linestyle=":", linewidth=1, label="true effect = 0.5")
    axes[1].set_xlabel("difference of means")
    axes[1].set_title(f"Bootstrap CI = [{np.quantile(boot_diffs, 0.025):.2f}, {np.quantile(boot_diffs, 0.975):.2f}]")
    axes[1].legend(fontsize=8)
    fig.suptitle("Loop C: continuous outcome (revenue) -- t-test and bootstrap agree")
    fig.tight_layout()
    out = IMG_DIR / "continuous_outcome.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_stratified_vs_pooled(manifest):
    """Two strata with different effects and different sizes; compare pooled vs per-stratum view."""
    apply_style()
    strata_sizes = {"power-users": 200, "casual": 1800}
    p_by_stratum = {"power-users": (0.30, 0.32), "casual": (0.05, 0.07)}
    strata = stratified_binary(strata_sizes, p_by_stratum, seed=SEEDS["stratified"])

    # Pooled view
    c_total = np.concatenate([s.control for s in strata.values()])
    t_total = np.concatenate([s.treatment for s in strata.values()])
    pooled = two_proportion_z(int(t_total.sum()), len(t_total), int(c_total.sum()), len(c_total))

    # Per-stratum view
    per_stratum = {}
    for name, s in strata.items():
        nc = len(s.control)
        nt = len(s.treatment)
        z = two_proportion_z(int(s.treatment.sum()), nt, int(s.control.sum()), nc)
        per_stratum[name] = (s.treatment.mean() - s.control.mean(), z.p_value, nc + nt)

    save_samples(np.array([list(strata_sizes.values())]), DATA_DIR / "strata_sizes", seed=SEEDS["stratified"], meta={"strata_sizes": strata_sizes, "p_by_stratum": p_by_stratum})

    fig, ax = plt.subplots(figsize=(9, 4.0))
    names = list(strata.keys()) + ["pooled"]
    diffs = [per_stratum[n][0] for n in strata.keys()] + [t_total.mean() - c_total.mean()]
    pvals = [per_stratum[n][1] for n in strata.keys()] + [pooled.p_value]
    sizes = [per_stratum[n][2] for n in strata.keys()] + [len(t_total) + len(c_total)]
    cmap = plt.get_cmap("viridis")
    bars = ax.bar(names, diffs, color=[cmap(i / max(1, len(names) - 1)) for i in range(len(names))])
    for b, d, p, s in zip(bars, diffs, pvals, sizes):
        ax.text(b.get_x() + b.get_width() / 2, d + 0.001, f"diff={d:.3f}\np={p:.3g}\nN={s}", ha="center", va="bottom", fontsize=8)
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_ylabel("treatment - control")
    ax.set_title("Loop D: per-stratum effects vs pooled (a preview of Simpson's-paradox territory)")
    fig.tight_layout()
    out = IMG_DIR / "stratified_vs_pooled.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_decision_rule():
    """Frequentist 'p<0.05' vs Bayesian 'P(effect > MMU) > 0.95'."""
    apply_style()
    n_runs = 300
    n_per_arm = 2000
    rng = np.random.default_rng(99)
    mmu = 0.005  # minimum meaningfull uplift = 0.5pp

    truths = np.linspace(-0.02, 0.04, 25)
    freq_ship = np.zeros_like(truths)
    bayes_ship = np.zeros_like(truths)
    for i, true_diff in enumerate(truths):
        for _ in range(n_runs):
            pc = 0.10
            pt = pc + true_diff
            if pt < 0 or pt > 1:
                continue
            exp = two_arm_binary(n_per_arm, pc, pt, seed=int(rng.integers(0, 2**30)))
            z = two_proportion_z(int(exp.treatment.sum()), n_per_arm, int(exp.control.sum()), n_per_arm)
            if z.p_value < 0.05 and z.point_estimate > 0:
                freq_ship[i] += 1
            a_c, b_c = 1 + int(exp.control.sum()), 1 + (n_per_arm - int(exp.control.sum()))
            a_t, b_t = 1 + int(exp.treatment.sum()), 1 + (n_per_arm - int(exp.treatment.sum()))
            local_rng = np.random.default_rng(0)
            diffs = local_rng.beta(a_t, b_t, 2000) - local_rng.beta(a_c, b_c, 2000)
            if (diffs > mmu).mean() > 0.95:
                bayes_ship[i] += 1
        freq_ship[i] /= n_runs
        bayes_ship[i] /= n_runs

    fig, ax = plt.subplots()
    ax.plot(truths, freq_ship, color=PALETTE["frequentist"], label="freq: p<0.05 and direction positive")
    ax.plot(truths, bayes_ship, color=PALETTE["bayesian"], label=f"Bayes: P(diff > {mmu}) > 0.95")
    ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1, label="no effect")
    ax.axvline(mmu, color=PALETTE["highlight"], linestyle=":", linewidth=1, label="MMU (minimum meaningful)")
    ax.set_xlabel("true effect (treatment minus control)")
    ax.set_ylabel("ship rate (over runs)")
    ax.set_ylim(0, 1.05)
    ax.set_title("Loop D: freq (H0: diff=0) vs Bayes (with MMU), shipping rate vs truth")
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = IMG_DIR / "decision_rule.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_pymc_posterior(manifest):
    """Same data as Loop A's N=10000 case, fit with PyMC. Closed-form Beta is also computed for comparison."""
    apply_style()
    n = 10000
    exp = two_arm_binary(n, p_control=0.05, p_treatment=0.06, seed=SEEDS["binary_large"])
    s_c = int(exp.control.sum())
    s_t = int(exp.treatment.sum())
    idata = two_arm_posterior(s_c, n, s_t, n, seed=SEEDS["pymc"], draws=2000, chains=2, tune=1000, progressbar=False)
    res = save_idata(idata, DATA_DIR / "two_arm_posterior", seed=SEEDS["pymc"], meta={"n_per_arm": n, "s_c": s_c, "s_t": s_t, "model": "Beta(1,1) priors per arm"})
    add_artifact(manifest, path=res.path, kind="idata", seed=SEEDS["pymc"], sha256=res.sha256, description="Two-arm Beta-Bernoulli PyMC posterior at N=10000")

    diff = idata.posterior["diff"].values.ravel()
    p_c_samples = idata.posterior["p_control"].values.ravel()
    p_t_samples = idata.posterior["p_treatment"].values.ravel()

    # Closed-form for cross-validation
    cf_c = np.random.default_rng(0).beta(1 + s_c, 1 + n - s_c, len(p_c_samples))
    cf_t = np.random.default_rng(1).beta(1 + s_t, 1 + n - s_t, len(p_t_samples))
    cf_diff = cf_t - cf_c

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0))
    axes[0].hist(p_c_samples, bins=50, alpha=0.55, color=PALETTE["frequentist"], label="p_control")
    axes[0].hist(p_t_samples, bins=50, alpha=0.55, color=PALETTE["bayesian"], label="p_treatment")
    axes[0].axvline(0.05, color=PALETTE["muted"], linestyle="--", linewidth=1, label="true p_c = 0.05")
    axes[0].axvline(0.06, color=PALETTE["muted"], linestyle=":", linewidth=1, label="true p_t = 0.06")
    axes[0].set_xlabel("p")
    axes[0].set_ylabel("samples")
    axes[0].set_title("PyMC per-arm posteriors")
    axes[0].legend(fontsize=8)

    axes[1].hist(diff, bins=50, density=True, alpha=0.7, color=PALETTE["bayesian"], label=f"PyMC posterior on diff (mean = {diff.mean():.4f})")
    axes[1].hist(cf_diff, bins=50, density=True, alpha=0.4, color=PALETTE["highlight"], histtype="step", linewidth=2, label="closed-form Beta diff (cross-check)")
    axes[1].axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[1].axvline(0.01, color=PALETTE["muted"], linestyle=":", linewidth=1, label="true diff = 0.01")
    axes[1].set_xlabel("treatment - control")
    axes[1].set_title(f"posterior on diff: P(diff > 0) = {(diff > 0).mean():.3f}")
    axes[1].legend(fontsize=8)

    fig.suptitle("Loop F: Bayesian two-arm A/B (PyMC) recovers the closed-form answer")
    fig.tight_layout()
    out = IMG_DIR / "pymc_two_arm.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_two_arm_binary(),
        render_continuous_outcome(),
        render_stratified_vs_pooled(manifest),
        render_decision_rule(),
        render_pymc_posterior(manifest),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 8 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 8: wrote {len(paths)} figures + 1 PyMC trace")


if __name__ == "__main__":
    main()
