"""Regenerate Chapter 17 (Attribution) story-track figures."""

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

CHAPTER = "17-attribution"
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


def render_attribution_comparison():
    apply_story_style()
    # 5 touches: YouTube ad, Instagram, Google search ad, email, organic visit (conversion)
    touches = ["YouTube\nad", "Instagram\npost", "Google\npaid search", "marketing\nemail", "organic\nvisit"]
    # Credit assigned by each model
    models = {
        "last-touch": [0, 0, 0, 0, 1.0],
        "first-touch": [1.0, 0, 0, 0, 0],
        "linear": [0.2, 0.2, 0.2, 0.2, 0.2],
        "time-decay": [0.03, 0.07, 0.15, 0.25, 0.50],
        "position-based": [0.40, 0.10, 0.10, 0.00, 0.40],
    }
    colors = [PALETTE["focus"], PALETTE["contrast"], PALETTE["support"], "#7a9b76", PALETTE["muted"]]
    fig, axes = plt.subplots(1, len(models), figsize=(14, 4.0), sharey=True)
    for ax, (name, credits), color in zip(axes, models.items(), colors):
        ax.bar(range(len(touches)), credits, color=color, width=0.8)
        ax.set_xticks(range(len(touches)))
        ax.set_xticklabels(touches, fontsize=8, rotation=10)
        ax.set_title(name, fontsize=9)
        ax.set_ylim(0, 1.05)
        if ax is axes[0]: ax.set_ylabel("fraction of credit")
    fig.suptitle("same five-touch path to conversion, five different credit assignments")
    out = IMG_DIR / "attribution_comparison.png"
    fig.savefig(out); plt.close(fig); return out


def render_holdout_vs_attributed():
    apply_story_style()
    channels = ["paid search\n(branded)", "display ads", "email", "social media"]
    attributed = [35, 18, 12, 8]
    holdout = [2, 14, 11, 7]  # effect from randomized holdout experiment
    x = np.arange(len(channels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(11, 4.5))
    bars_att = ax.bar(x - width/2, attributed, width=width, color=PALETTE["focus"], label="last-touch attributed")
    bars_hold = ax.bar(x + width/2, holdout, width=width, color=PALETTE["contrast"], label="randomized holdout (causal)")
    for b, v in zip(bars_att, attributed):
        ax.text(b.get_x() + b.get_width()/2, v + 0.5, str(v), ha="center", fontsize=9)
    for b, v in zip(bars_hold, holdout):
        ax.text(b.get_x() + b.get_width()/2, v + 0.5, str(v), ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(channels)
    ax.set_ylabel("conversions attributed / caused (per 1000 users)")
    ax.set_title("branded paid search: last-touch claims 35 conversions, holdout shows most are organic anyway")
    ax.legend()
    out = IMG_DIR / "holdout_vs_attributed.png"
    fig.savefig(out); plt.close(fig); return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [(render_attribution_comparison(), "derived", "Story Ch.17: five attribution models on same path"),
             (render_holdout_vs_attributed(), "derived", "Story Ch.17: last-touch vs holdout causal estimate")]
    for path, seed, desc in paths:
        add_artifact(manifest, path=path, kind="image", seed=seed, sha256=_sha256_file(path), description=desc)
    save_manifest(manifest)
    print(f"Story Ch.17: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
