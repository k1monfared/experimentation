"""Regenerate Chapter 13 figures: metric tree."""

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

CHAPTER = "13-metric-tree"
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


def render_predictivity():
    apply_story_style()
    rng = np.random.default_rng(0)
    n = 200
    true_effect = rng.normal(0, 1, size=n)
    short_term = true_effect + rng.normal(0, 2.5, size=n)
    long_term = true_effect + rng.normal(0, 0.5, size=n)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.scatter(short_term, long_term, color=PALETTE["focus"], alpha=0.55, s=30)
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    r = np.corrcoef(short_term, long_term)[0, 1]
    ax.set_xlabel("short-term metric (cheap to measure)")
    ax.set_ylabel("long-term metric (what we care about)")
    ax.set_title(f"200 experiments. Correlation r = {r:.2f}, R^2 = {r*r:.2f}")
    out = IMG_DIR / "predictivity.png"
    fig.savefig(out); plt.close(fig); return out


def render_proxy_quality():
    apply_story_style()
    rng = np.random.default_rng(1)
    n = 100
    true_effect = rng.normal(0, 1, size=n)
    clean = true_effect + rng.normal(0, 0.5, size=n)
    noisy = true_effect + rng.normal(0, 2.0, size=n)
    lying = -true_effect + rng.normal(0, 1.5, size=n)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.0), sharey=True)
    for ax, (label, proxy, color) in zip(axes, [
        ("clean proxy", clean, PALETTE["focus"]),
        ("noisy proxy", noisy, PALETTE["contrast"]),
        ("lying proxy", lying, "#9a6f9c"),
    ]):
        ax.scatter(proxy, true_effect, color=color, alpha=0.55, s=30)
        r = np.corrcoef(proxy, true_effect)[0, 1]
        ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.set_xlabel(f"{label}")
        if ax is axes[0]:
            ax.set_ylabel("true effect")
        ax.set_title(f"r = {r:+.2f}")
    out = IMG_DIR / "proxy_quality.png"
    fig.savefig(out); plt.close(fig); return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = []
    paths.append((render_predictivity(), 0, "Story Ch.13: short-term vs long-term metric scatter"))
    paths.append((render_proxy_quality(), 1, "Story Ch.13: clean vs noisy vs lying proxy"))
    for path, seed, desc in paths:
        add_artifact(manifest, path=path, kind="image", seed=seed, sha256=_sha256_file(path), description=desc)
    save_manifest(manifest)
    print(f"Story Ch.13: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
