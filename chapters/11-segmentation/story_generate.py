"""Regenerate Chapter 11 figures: segmentation."""

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

CHAPTER = "11-segmentation"
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


def render_demographic_vs_behavioral():
    apply_story_style()
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), sharey=True)

    # Demographic: country (no real signal)
    countries = ["country A", "country B", "country C"]
    country_lifts = [3.2, 3.4, 2.8]
    axes[0].bar(countries, country_lifts, color=PALETTE["muted"], width=0.65)
    for i, v in enumerate(country_lifts):
        axes[0].text(i, v + 0.2, f"+{v:.1f}pp", ha="center", fontsize=10)
    axes[0].axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[0].set_ylabel("treatment lift (percentage points)")
    axes[0].set_title("by country: roughly equal, no signal")
    axes[0].set_ylim(-6, 14)

    # Behavioural segments: real heterogeneity
    segments = ["active\ncontributor", "active\nconsumer", "silent\nintentional", "passive\nconsumer"]
    segment_lifts = [10.0, 4.0, -3.0, 0.0]
    colors = [PALETTE["focus"], PALETTE["contrast"], "#9a6f9c", PALETTE["muted"]]
    bars = axes[1].bar(segments, segment_lifts, color=colors, width=0.65)
    for b, v in zip(bars, segment_lifts):
        axes[1].text(b.get_x() + b.get_width() / 2, v + (0.4 if v >= 0 else -0.8),
                     f"{v:+.1f}pp", ha="center", fontsize=10)
    axes[1].axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[1].set_title("by behaviour: huge heterogeneity, some segments lose")
    axes[1].set_ylim(-6, 14)
    out = IMG_DIR / "demographic_vs_behavioral.png"
    fig.savefig(out); plt.close(fig); return out


def render_segment_signatures():
    """Three behavioral axes for each segment."""
    apply_story_style()
    rng = np.random.default_rng(0)
    n = 1000
    # Simulate segment characteristics
    segments_data = {
        "active contributor": {"active": 0.85, "contribute": 0.7, "intent": 0.65},
        "active consumer": {"active": 0.75, "contribute": 0.15, "intent": 0.6},
        "silent intentional": {"active": 0.25, "contribute": 0.1, "intent": 0.55},
        "passive consumer": {"active": 0.3, "contribute": 0.1, "intent": 0.25},
    }
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.0), sharey=False)
    axis_names = ["weekly active rate", "contribution rate", "intentional rate"]
    keys = ["active", "contribute", "intent"]
    colors = [PALETTE["focus"], PALETTE["contrast"], "#9a6f9c", PALETTE["muted"]]
    for ax, axis_name, key in zip(axes, axis_names, keys):
        for (seg, props), color in zip(segments_data.items(), colors):
            mu, sigma = props[key], 0.12
            samples = np.clip(rng.normal(mu, sigma, size=n), 0, 1)
            ax.hist(samples, bins=40, alpha=0.55, color=color, label=seg)
        ax.set_xlabel(axis_name)
        if ax is axes[0]:
            ax.set_ylabel("number of users")
            ax.legend(fontsize=8)
    fig.suptitle("each segment has a distinctive signature on the three axes")
    out = IMG_DIR / "segment_signatures.png"
    fig.savefig(out); plt.close(fig); return out


def render_segmentation_choices():
    """Three segmentation schemes, same data, different stories."""
    apply_story_style()
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.0), sharey=True)
    # Tenure: weak heterogeneity
    axes[0].bar(["new", "veteran"], [3.0, 4.5], color=PALETTE["muted"], width=0.55)
    axes[0].set_title("tenure: minor difference")
    axes[0].set_ylim(-2, 12)
    # Activity tertile: clear gradient
    axes[1].bar(["low", "medium", "high"], [-0.5, 4.0, 9.0],
                color=[PALETTE["muted"], PALETTE["contrast"], PALETTE["focus"]], width=0.55)
    axes[1].set_title("activity tertile: clear gradient")
    # Behavioural label
    axes[2].bar(["passive", "silent\nintentional", "active\nconsumer", "active\ncontributor"],
                [0.0, -3.0, 4.0, 10.0],
                color=[PALETTE["muted"], "#9a6f9c", PALETTE["contrast"], PALETTE["focus"]], width=0.55)
    axes[2].set_title("behavioural label: nuanced")
    for ax in axes:
        ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.set_ylabel("treatment lift (pp)")
    out = IMG_DIR / "segmentation_choices.png"
    fig.savefig(out); plt.close(fig); return out


def main():
    ensure_dirs()
    paths = []
    paths.append((render_demographic_vs_behavioral(), "derived",
                  "Story Ch.11: demographic (country) vs behavioural segments"))
    paths.append((render_segment_signatures(), 0,
                  "Story Ch.11: behavioral segment signatures across three axes"))
    paths.append((render_segmentation_choices(), "derived",
                  "Story Ch.11: three segmentation schemes, three stories"))
    print(f"Story Ch.11: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
