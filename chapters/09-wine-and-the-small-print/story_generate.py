"""Regenerate Chapter 9 (Who got studied, what got measured) figures.

Four traps: external validity, outcome choice, side effects, weighting.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.plot.story import PALETTE, apply_story_style, reference_line  # noqa: E402

CHAPTER = "09-wine-and-the-small-print"
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


def render_external_validity():
    """Per-segment effects vs the studied effect."""
    apply_story_style()
    segments = ["22yo students\n(studied)", "40yo under stress",
                "65+ healthy", "pregnant women", "teens", "middle-aged sedentary"]
    effects = [0.05, -0.02, 0.01, -0.10, -0.05, 0.0]
    colors = [PALETTE["focus"] if e == 0.05 else (PALETTE["contrast"] if e > 0
              else (PALETTE["support"] if e == 0 else "#9a6f9c")) for e in effects]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    bars = ax.bar(segments, [e * 100 for e in effects], color=colors, width=0.7)
    for b, e in zip(bars, effects):
        y = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, y + (1 if y > 0 else -1.5),
                f"{y:+.0f}pp", ha="center", fontsize=9)
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_xticklabels(segments, rotation=15, ha="right", fontsize=9)
    ax.set_ylabel("treatment effect (percentage points)")
    ax.set_ylim(-15, 10)
    ax.set_title("studied: 22yo students show +5pp benefit. Real population: mixed, often negative.")
    out = IMG_DIR / "external_validity.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_outcome_choice():
    """Three different outcomes, three different verdicts."""
    apply_story_style()
    outcomes = ["resting heart rate\n(proxy)",
                "exercise tolerance\n(proxy)",
                "all-cause mortality\n(what I actually care about)"]
    estimates = [-3.0, 1.0, -0.2]
    cis = [(-5.0, -1.0), (-1.0, 3.0), (-1.0, 0.6)]
    colors = [PALETTE["focus"], PALETTE["contrast"], PALETTE["ink"]]

    fig, ax = plt.subplots(figsize=(11, 4.5))
    for i, (label, est, ci, c) in enumerate(zip(outcomes, estimates, cis, colors)):
        ax.errorbar(est, i, xerr=[[est - ci[0]], [ci[1] - est]], fmt="o", color=c,
                    markersize=10, capsize=8, linewidth=2)
        ax.text(est, i + 0.15, f"{est:+.1f}%", ha="center", fontsize=9, color=c)
    ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_yticks(range(len(outcomes)))
    ax.set_yticklabels(outcomes)
    ax.set_xlabel("treatment effect (%)")
    ax.set_title("three outcomes from one study. Headlines pick the publishable one.")
    out = IMG_DIR / "outcome_choice.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_side_effects_tradeoff():
    """Two-panel: side-effect picture and tradeoff utility curve."""
    apply_story_style()
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

    # Panel 1: target, secondary, harm
    metrics = ["target metric", "secondary metric", "harm metric"]
    effects = [0.30, 0.0, -0.40]
    colors = [PALETTE["focus"], PALETTE["muted"], "#9a6f9c"]
    bars = axes[0].bar(metrics, effects, color=colors, width=0.6)
    for b, e in zip(bars, effects):
        y = b.get_height()
        axes[0].text(b.get_x() + b.get_width() / 2, y + (0.02 if y > 0 else -0.04),
                     f"{y:+.2f}", ha="center", fontsize=10)
    axes[0].axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[0].set_ylabel("effect size (standard units)")
    axes[0].set_ylim(-0.5, 0.5)
    axes[0].set_title("the intervention helps target, hurts harm metric by more")

    # Panel 2: utility curve
    ws = np.linspace(0, 1, 200)
    u = ws * 0.30 + (1 - ws) * (-0.40)
    axes[1].plot(ws, u, color=PALETTE["focus"], linewidth=2)
    axes[1].axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    boundary = 0.40 / (0.30 + 0.40)
    axes[1].axvline(boundary, color=PALETTE["ink"], linestyle=":", linewidth=1,
                    label=f"boundary at w = {boundary:.2f}")
    axes[1].set_xlabel("weight on target metric (vs 1 - w on harm)")
    axes[1].set_ylabel("utility = w * target + (1 - w) * harm")
    axes[1].set_title("two stakeholders with different weights, different decisions")
    axes[1].legend()

    out = IMG_DIR / "side_effects_tradeoff.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    paths = []
    paths.append((render_external_validity(), "derived",
                  "Story Ch.9: per-segment effects vs studied cohort"))
    paths.append((render_outcome_choice(), "derived",
                  "Story Ch.9: three outcomes, three verdicts"))
    paths.append((render_side_effects_tradeoff(), "derived",
                  "Story Ch.9: target vs harm + utility weighting"))
    print(f"Story Ch.9: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
