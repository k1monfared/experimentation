"""Regenerate Chapter 12 figures: Simpson's paradox."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.plot.story import PALETTE, apply_story_style  # noqa: E402

CHAPTER = "12-simpsons-paradox"
CHAPTER_DIR = Path(__file__).resolve().parent
IMG_DIR = CHAPTER_DIR / "images" / "story"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.yaml"


def ensure_dirs(): IMG_DIR.mkdir(parents=True, exist_ok=True)
def load_manifest():
    if MANIFEST_PATH.exists(): return yaml.safe_load(MANIFEST_PATH.read_text()) or {"artifacts": []}
    return {"artifacts": []}
def save_manifest(m): MANIFEST_PATH.write_text(yaml.safe_dump(m, sort_keys=False))
def add_artifact(m, *, path, kind, seed, sha256, description):
    rel = str(path.relative_to(REPO_ROOT))
    m["artifacts"] = [a for a in m["artifacts"] if a.get("path") != rel]
    m["artifacts"].append({"path": rel, "chapter": CHAPTER, "kind": kind, "seed": seed, "sha256": sha256, "description": description})


def render_paradox_construction():
    apply_story_style()
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

    # Per-segment view: each segment +5pp
    segments = ["segment A\n(small, high baseline)", "segment B\n(large, low baseline)"]
    control = [0.80, 0.20]
    treatment = [0.85, 0.25]
    x = np.arange(len(segments))
    width = 0.35
    axes[0].bar(x - width/2, control, width=width, color=PALETTE["contrast"], label="control")
    axes[0].bar(x + width/2, treatment, width=width, color=PALETTE["focus"], label="treatment")
    for i, (c, t) in enumerate(zip(control, treatment)):
        axes[0].text(i - width/2, c + 0.02, f"{c:.2f}", ha="center", fontsize=9)
        axes[0].text(i + width/2, t + 0.02, f"{t:.2f}", ha="center", fontsize=9)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(segments)
    axes[0].set_ylabel("outcome rate")
    axes[0].set_title("per segment: each up by +5pp")
    axes[0].set_ylim(0, 1.05)
    axes[0].legend()

    # Aggregate view: the lie
    axes[1].bar(["aggregate\ncontrol", "aggregate\ntreatment"], [0.500, 0.285],
                color=[PALETTE["contrast"], PALETTE["focus"]], width=0.5)
    for i, v in enumerate([0.500, 0.285]):
        axes[1].text(i, v + 0.02, f"{v:.3f}", ha="center", fontsize=10)
    axes[1].set_ylabel("outcome rate")
    axes[1].set_title("aggregate: -21pp difference (treatment looks WORSE)")
    axes[1].set_ylim(0, 1.05)

    out = IMG_DIR / "paradox_construction.png"
    fig.savefig(out); plt.close(fig); return out


def render_paradox_sweep():
    """Sweep treatment share and watch aggregate effect drift."""
    apply_story_style()
    p_a, p_b = 0.80, 0.20
    seg_a_frac = 0.20
    lift = 0.05
    treat_in_a_grid = np.linspace(0.05, 0.95, 50)
    aggregate_effects = []
    for t_a in treat_in_a_grid:
        t_b = 1 - t_a
        n_per_seg = 1000
        n_a, n_b = int(n_per_seg * seg_a_frac * 5), int(n_per_seg * (1 - seg_a_frac) * 5)
        # Treatment counts in each segment
        t_a_count = int(n_a * t_a)
        c_a_count = n_a - t_a_count
        t_b_count = int(n_b * t_b)
        c_b_count = n_b - t_b_count
        if c_a_count == 0 or t_a_count == 0 or c_b_count == 0 or t_b_count == 0:
            aggregate_effects.append(np.nan)
            continue
        # Aggregate
        treat_total = t_a_count + t_b_count
        ctrl_total = c_a_count + c_b_count
        treat_outcome = t_a_count * (p_a + lift) + t_b_count * (p_b + lift)
        ctrl_outcome = c_a_count * p_a + c_b_count * p_b
        agg_diff = treat_outcome / treat_total - ctrl_outcome / ctrl_total
        aggregate_effects.append(agg_diff)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(treat_in_a_grid, aggregate_effects, color=PALETTE["focus"], linewidth=2, label="aggregate effect")
    ax.axhline(0.05, color=PALETTE["ink"], linestyle="--", linewidth=1, label="true within-segment effect (+5pp)")
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_xlabel("share of segment A users assigned to treatment")
    ax.set_ylabel("aggregate effect")
    ax.legend()
    ax.set_title("the aggregate flips sign as assignment becomes imbalanced")
    out = IMG_DIR / "paradox_sweep.png"
    fig.savefig(out); plt.close(fig); return out


def render_berkeley_style():
    """Two-department admissions example."""
    apply_story_style()
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

    # Per department: women have slight edge
    depts = ["Department A\n(hard, ~20%)", "Department B\n(easy, ~65%)"]
    men = [0.18, 0.62]
    women = [0.22, 0.66]
    x = np.arange(len(depts))
    width = 0.35
    axes[0].bar(x - width/2, men, width=width, color=PALETTE["contrast"], label="men")
    axes[0].bar(x + width/2, women, width=width, color=PALETTE["focus"], label="women")
    for i, (m, w) in enumerate(zip(men, women)):
        axes[0].text(i - width/2, m + 0.02, f"{m:.0%}", ha="center", fontsize=9)
        axes[0].text(i + width/2, w + 0.02, f"{w:.0%}", ha="center", fontsize=9)
    axes[0].set_xticks(x); axes[0].set_xticklabels(depts)
    axes[0].set_ylabel("acceptance rate")
    axes[0].set_title("per department: women have slight edge")
    axes[0].set_ylim(0, 0.8)
    axes[0].legend()

    # Aggregate: men higher (because most men applied to easy dept)
    # Suppose 90% men apply to B, 90% women apply to A
    # Men: 100*0.9*0.62 + 100*0.1*0.18 = 55.8 + 1.8 = 57.6 → 57.6%
    # Women: 100*0.9*0.22 + 100*0.1*0.66 = 19.8 + 6.6 = 26.4 → 26.4%
    aggregate = [0.576, 0.264]
    axes[1].bar(["men\n(aggregate)", "women\n(aggregate)"], aggregate,
                color=[PALETTE["contrast"], PALETTE["focus"]], width=0.5)
    for i, v in enumerate(aggregate):
        axes[1].text(i, v + 0.02, f"{v:.0%}", ha="center", fontsize=10)
    axes[1].set_ylabel("acceptance rate")
    axes[1].set_title("aggregate: men accepted at higher rate")
    axes[1].set_ylim(0, 0.8)

    out = IMG_DIR / "berkeley_style.png"
    fig.savefig(out); plt.close(fig); return out


def main():
    ensure_dirs()
    paths = []
    paths.append((render_paradox_construction(), "derived",
                  "Story Ch.12: paradox construction, segment vs aggregate views"))
    paths.append((render_paradox_sweep(), "derived",
                  "Story Ch.12: aggregate effect as a function of assignment imbalance"))
    paths.append((render_berkeley_style(), "derived",
                  "Story Ch.12: Berkeley-style admissions example"))
    print(f"Story Ch.12: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
