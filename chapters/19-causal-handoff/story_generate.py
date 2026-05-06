"""Regenerate Chapter 19 (Causal handoff) story-track figures."""

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

CHAPTER = "19-causal-handoff"
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


def render_selection_bias():
    apply_story_style()
    rng = np.random.default_rng(19)
    n = 2000
    propensity = rng.normal(0, 1, size=n)
    treatment = rng.random(n) < 1 / (1 + np.exp(-propensity))
    true_effect = 0.30
    outcome = propensity + true_effect * treatment + rng.normal(0, 0.5, size=n)

    treated_mean = outcome[treatment].mean()
    untreated_mean = outcome[~treatment].mean()
    naive_diff = treated_mean - untreated_mean

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    axes[0].scatter(propensity[~treatment], outcome[~treatment], alpha=0.3, s=8,
                    color=PALETTE["contrast"], label=f"control (mean={untreated_mean:.2f})")
    axes[0].scatter(propensity[treatment], outcome[treatment], alpha=0.3, s=8,
                    color=PALETTE["focus"], label=f"treated (mean={treated_mean:.2f})")
    axes[0].set_xlabel("propensity (e.g. health, motivation)")
    axes[0].set_ylabel("outcome")
    axes[0].set_title(f"naive difference = {naive_diff:.2f} (true effect = {true_effect})")
    axes[0].legend(fontsize=8)

    bars = axes[1].bar(["naive\ncomparison", "true causal\neffect"], [naive_diff, true_effect],
                       color=[PALETTE["focus"], PALETTE["muted"]], width=0.5)
    for b, v in zip(bars, [naive_diff, true_effect]):
        axes[1].text(b.get_x() + b.get_width()/2, v + 0.02, f"{v:+.2f}",
                     ha="center", fontsize=12)
    axes[1].axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[1].set_ylabel("effect estimate")
    axes[1].set_title("the naive number is more than 3x the truth")
    out = IMG_DIR / "selection_bias.png"
    fig.savefig(out); plt.close(fig)
    return out, {"naive": round(naive_diff, 3), "true": true_effect}


def main():
    ensure_dirs()
    manifest = load_manifest()
    p1, nums = render_selection_bias()
    paths = [(p1, 19, f"Story Ch.19: selection bias demo, naive={nums['naive']}, true={nums['true']}")]
    for path, seed, desc in paths:
        add_artifact(manifest, path=path, kind="image", seed=seed, sha256=_sha256_file(path), description=desc)
    save_manifest(manifest)
    print(f"Story Ch.19: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
