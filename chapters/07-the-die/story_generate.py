"""Regenerate Chapter 7 (More than two outcomes) story-track figures.

Generalize the binary-coin framework to many outcomes via the die.
Show counts wobbling, the multiple-comparisons trap, and the Bayesian
joint posterior that sidesteps it.
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

CHAPTER = "07-the-die"
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


def render_face_counts_wobble():
    """At N=60, 600, 6000 rolls of a fair die, what do face counts look like?"""
    apply_story_style()
    rng = np.random.default_rng(72)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.0), sharey=False)
    for ax, n in zip(axes, [60, 600, 6000]):
        rolls = rng.choice(6, size=n)
        counts = np.bincount(rolls, minlength=6)
        ax.bar(np.arange(1, 7), counts, color=PALETTE["focus"], width=0.85)
        expected = n / 6
        ax.axhline(expected, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.set_xlabel("face")
        ax.set_ylabel(f"count")
        ax.set_title(f"{n} rolls (each face expected: {expected:.0f})")
        for i, c in enumerate(counts):
            ax.text(i + 1, c + n * 0.005, str(c), ha="center", fontsize=9)
    out = IMG_DIR / "face_counts_wobble.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_multiple_comparisons_trap():
    """Test each face independently. How often does at least one falsely fire?"""
    apply_story_style()
    rng = np.random.default_rng(72)
    n_per_die = 600
    n_dice = 1000

    naive_flagged = 0
    bonferroni_flagged = 0
    for _ in range(n_dice):
        rolls = rng.choice(6, size=n_per_die)
        counts = np.bincount(rolls, minlength=6)
        any_naive = False
        any_bonf = False
        for c in counts:
            pval = stats.binomtest(int(c), n_per_die, p=1/6, alternative="two-sided").pvalue
            if pval < 0.05:
                any_naive = True
            if pval < 0.05 / 6:
                any_bonf = True
        if any_naive:
            naive_flagged += 1
        if any_bonf:
            bonferroni_flagged += 1

    naive_rate = naive_flagged / n_dice
    bonf_rate = bonferroni_flagged / n_dice

    fig, ax = plt.subplots(figsize=(11, 4.5))
    bars = ax.bar(["test each face\nat 5%",
                   "test each face\nat 5%/6 (Bonferroni)",
                   "what 5% promised"],
                  [naive_rate, bonf_rate, 0.05],
                  color=[PALETTE["focus"], PALETTE["contrast"], PALETTE["muted"]],
                  width=0.6)
    for b, v in zip(bars, [naive_rate, bonf_rate, 0.05]):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.005, f"{v * 100:.1f}%",
                ha="center", fontsize=10)
    ax.set_ylabel(f"fraction of fair-die experiments where\nat least one face was wrongly flagged")
    ax.set_ylim(0, max(naive_rate, 0.05) * 1.4)
    ax.set_title(f"with 6 simultaneous tests, the 5% promise gets violated")
    out = IMG_DIR / "multiple_comparisons_trap.png"
    fig.savefig(out)
    plt.close(fig)
    return out, naive_rate, bonf_rate


def render_dirichlet_posterior():
    """Loaded die: face-6 has p=1/3, others 2/15. After 600 rolls, marginal posteriors."""
    apply_story_style()
    rng = np.random.default_rng(72)
    n = 600
    p_loaded = [2/15, 2/15, 2/15, 2/15, 2/15, 1/3]
    rolls = rng.choice(6, size=n, p=p_loaded)
    counts = np.bincount(rolls, minlength=6)
    # Dirichlet(1+c1, ..., 1+c6) posterior. Marginal for each face is Beta(1+ci, 1 + n - ci).
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ps = np.linspace(0, 0.5, 1000)
    colors = [PALETTE["focus"], PALETTE["contrast"], PALETTE["support"], "#7a9b76",
              PALETTE["ink"], PALETTE["muted"]]
    for i in range(6):
        marginal = stats.beta.pdf(ps, 1 + counts[i], 1 + n - counts[i])
        ax.plot(ps, marginal, color=colors[i], linewidth=1.8, label=f"face {i+1}: {counts[i]} rolls")
    ax.axvline(1/6, color=PALETTE["ink"], linestyle="--", linewidth=1, label="fair value 1/6")
    ax.set_xlim(0, 0.5)
    ax.set_xlabel("possible probability of this face")
    ax.set_ylabel("strength of belief")
    ax.set_title(f"after {n} rolls of a die loaded toward face 6")
    ax.legend(loc="upper right", fontsize=8)
    out = IMG_DIR / "dirichlet_posterior.png"
    fig.savefig(out)
    plt.close(fig)
    return out, counts.tolist()


def render_chi_square_pvalues():
    """As N grows, the chi-square test of fairness for the loaded die"""
    apply_story_style()
    rng = np.random.default_rng(72)
    p_loaded = [2/15, 2/15, 2/15, 2/15, 2/15, 1/3]
    sizes = np.unique(np.round(np.geomspace(30, 5000, 80)).astype(int))
    fair_p = []
    loaded_p = []
    for n in sizes:
        rolls_fair = rng.choice(6, size=n)
        counts_fair = np.bincount(rolls_fair, minlength=6)
        chi2_fair, pf = stats.chisquare(counts_fair, [n/6]*6)[:2]
        fair_p.append(pf)

        rolls_load = rng.choice(6, size=n, p=p_loaded)
        counts_load = np.bincount(rolls_load, minlength=6)
        chi2_load, pl = stats.chisquare(counts_load, [n/6]*6)[:2]
        loaded_p.append(pl)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(sizes, fair_p, color=PALETTE["contrast"], linewidth=1.8, label="fair die")
    ax.plot(sizes, loaded_p, color=PALETTE["focus"], linewidth=1.8, label="loaded die (face 6 doubled)")
    reference_line(ax, 0.05, label="alpha = 0.05")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(30, 5000)
    ax.set_ylim(1e-30, 2)
    ax.set_xlabel("number of rolls (log scale)")
    ax.set_ylabel("p-value (log scale)")
    ax.legend(loc="lower left")
    ax.set_title("chi-square test catches the loaded die as data grows")
    out = IMG_DIR / "chi_square_pvalues.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = []
    paths.append((render_face_counts_wobble(), 72,
                  "Story Ch.7: face counts at N=60, 600, 6000 rolls of fair die"))
    p_mc, naive, bonf = render_multiple_comparisons_trap()
    paths.append((p_mc, 72,
                  f"Story Ch.7: multiple-comparisons trap, naive {naive:.3f} vs Bonferroni {bonf:.3f}"))
    p_dir, dir_counts = render_dirichlet_posterior()
    paths.append((p_dir, 72,
                  f"Story Ch.7: Dirichlet posterior marginals after 600 rolls of loaded die, counts {dir_counts}"))
    paths.append((render_chi_square_pvalues(), 72,
                  "Story Ch.7: chi-square p-values vs N for fair and loaded die"))
    for path, seed, desc in paths:
        add_artifact(manifest, path=path, kind="image", seed=seed,
                     sha256=_sha256_file(path), description=desc)
    save_manifest(manifest)
    print(f"Story Ch.7: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
