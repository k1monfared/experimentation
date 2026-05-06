"""Regenerate Chapter 8 (From dice to A/B tests) story-track figures.

Two-arm comparison: binary outcome, continuous outcome, decision rules.
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

CHAPTER = "08-from-dice-to-ab"
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


def two_prop_z(s_t, n_t, s_c, n_c):
    """Two-proportion z-test (pooled SE)."""
    p_pool = (s_t + s_c) / (n_t + n_c)
    se = np.sqrt(p_pool * (1 - p_pool) * (1/n_t + 1/n_c))
    diff = s_t/n_t - s_c/n_c
    z = diff / se if se > 0 else 0
    p = 2 * stats.norm.sf(abs(z))
    return diff, z, p


def render_two_arm_at_two_sizes():
    """Same effect (5% vs 6%), two sample sizes, two views (frequentist + Bayesian)."""
    apply_story_style()
    rng = np.random.default_rng(8)
    p_c, p_t = 0.05, 0.06
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.0), sharey=False)
    for ax, n_per_arm in zip(axes, [1000, 10000]):
        s_c = rng.binomial(n_per_arm, p_c)
        s_t = rng.binomial(n_per_arm, p_t)
        diff, z, p = two_prop_z(s_t, n_per_arm, s_c, n_per_arm)
        # Bayesian posterior on diff via sampling
        rng2 = np.random.default_rng(8)
        samples_c = rng2.beta(1 + s_c, 1 + n_per_arm - s_c, size=20000)
        samples_t = rng2.beta(1 + s_t, 1 + n_per_arm - s_t, size=20000)
        diff_samples = samples_t - samples_c
        ax.hist(diff_samples, bins=60, density=True, color=PALETTE["focus"],
                alpha=0.55, label="belief curve over (treatment - control)")
        ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1, label="no difference")
        ax.axvline(p_t - p_c, color=PALETTE["ink"], linestyle=":", linewidth=1, label="true difference (0.01)")
        prob_pos = float((diff_samples > 0).mean())
        ax.set_xlabel("treatment rate minus control rate")
        ax.set_ylabel("strength of belief")
        ax.set_title(f"{n_per_arm} users per arm\n"
                     f"frequentist: p = {p:.3f}, observed diff = {diff:.4f}\n"
                     f"belief curve: P(treatment > control) = {prob_pos:.3f}")
        if ax is axes[0]:
            ax.legend(fontsize=8, loc="upper left")
    out = IMG_DIR / "two_arm_at_two_sizes.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_continuous_outcome():
    """Two-arm comparison on revenue per user."""
    apply_story_style()
    rng = np.random.default_rng(80)
    n = 2000
    mu_c, mu_t, sigma = 10.0, 10.5, 4.0
    rev_c = rng.normal(mu_c, sigma, size=n)
    rev_t = rng.normal(mu_t, sigma, size=n)
    t, p = stats.ttest_ind(rev_t, rev_c, equal_var=False)
    diff = rev_t.mean() - rev_c.mean()

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.hist(rev_c, bins=50, density=True, alpha=0.55, color=PALETTE["contrast"],
            label=f"control (mean {rev_c.mean():.2f})")
    ax.hist(rev_t, bins=50, density=True, alpha=0.55, color=PALETTE["focus"],
            label=f"treatment (mean {rev_t.mean():.2f})")
    ax.axvline(rev_c.mean(), color=PALETTE["contrast"], linestyle="-", linewidth=1.2)
    ax.axvline(rev_t.mean(), color=PALETTE["focus"], linestyle="-", linewidth=1.2)
    ax.set_xlabel("revenue per user")
    ax.set_ylabel("density")
    ax.set_title(f"revenue distributions, {n} per arm. Welch t: p = {p:.4f}, diff = {diff:.3f}")
    ax.legend()
    out = IMG_DIR / "continuous_outcome.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_decision_rules():
    """Frequentist vs Bayesian shipping rates across true effect sizes."""
    apply_story_style()
    rng = np.random.default_rng(8)
    n = 2000
    mmu = 0.005  # minimum meaningful uplift = 0.5pp
    p_c = 0.05
    n_trials = 300
    effects = np.linspace(-0.02, 0.04, 13)
    freq_ship = []
    bayes_ship = []
    for eff in effects:
        p_t = p_c + eff
        f = b = 0
        for _ in range(n_trials):
            s_c = rng.binomial(n, p_c)
            s_t = rng.binomial(n, p_t)
            diff_obs = s_t/n - s_c/n
            _, _, p = two_prop_z(s_t, n, s_c, n)
            # Frequentist rule
            if p < 0.05 and diff_obs > 0:
                f += 1
            # Bayesian rule: P(diff > MMU) > 0.95
            samples_c = rng.beta(1 + s_c, 1 + n - s_c, size=4000)
            samples_t = rng.beta(1 + s_t, 1 + n - s_t, size=4000)
            prob = float((samples_t - samples_c > mmu).mean())
            if prob > 0.95:
                b += 1
        freq_ship.append(f / n_trials)
        bayes_ship.append(b / n_trials)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(effects * 100, freq_ship, "o-", color=PALETTE["focus"],
            linewidth=1.8, label="frequentist (p<0.05 & positive)")
    ax.plot(effects * 100, bayes_ship, "s-", color=PALETTE["contrast"],
            linewidth=1.8, label=f"Bayesian (P(diff>{mmu*100:.1f}pp)>0.95)")
    ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.axvline(mmu * 100, color=PALETTE["ink"], linestyle=":", linewidth=1, label=f"MMU = {mmu*100:.1f}pp")
    ax.set_xlabel("true effect (percentage points lift)")
    ax.set_ylabel("fraction of experiments where rule says 'ship'")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title(f"shipping rates, {n} users per arm, {n_trials} simulated experiments per truth")
    out = IMG_DIR / "decision_rules.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    paths = []
    paths.append((render_two_arm_at_two_sizes(), 8,
                  "Story Ch.8: same effect at two sample sizes, frequentist + belief curve"))
    paths.append((render_continuous_outcome(), 80,
                  "Story Ch.8: continuous outcome (revenue per user) two-arm test"))
    paths.append((render_decision_rules(), 8,
                  "Story Ch.8: shipping decision rates, freq vs Bayes with MMU"))
    print(f"Story Ch.8: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
