"""Regenerate Chapter 14 (Novelty effects) story-track figures."""

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

CHAPTER = "14-novelty"
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


def render_novelty_lifecycle():
    apply_story_style()
    days = np.arange(0, 61)
    click_lift = 0.10 * np.exp(-days / 8)
    retention = -0.04 * (1 - np.exp(-days / 18))
    revenue = 0.03 * np.exp(-days / 10) - 0.02 * (1 - np.exp(-days / 25))

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(days, click_lift * 100, color=PALETTE["focus"], linewidth=2, label="click-rate lift (fast rise, fast decay)")
    ax.plot(days, retention * 100, color="#9a6f9c", linewidth=2, label="retention change (slow decay builds)")
    ax.plot(days, revenue * 100, color=PALETTE["contrast"], linewidth=2, linestyle="-.", label="revenue per user (crosses zero around day 35)")
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.axvline(7, color=PALETTE["ink"], linestyle=":", linewidth=1, label="typical 7-day test window")
    ax.set_xlabel("days since launch")
    ax.set_ylabel("effect (%)")
    ax.set_title("novelty effects: click win is visible at day 7, revenue and retention damage are still building")
    ax.legend(fontsize=8, loc="upper right")
    out = IMG_DIR / "novelty_lifecycle.png"
    fig.savefig(out); plt.close(fig); return out


def render_three_measurement_schemes():
    apply_story_style()
    rng = np.random.default_rng(14)
    n_users = 500
    n_days = 60
    base_rate = 0.20
    lift = 0.10
    half_life = 7

    rows = {"calendar": [], "since_exposure": [], "exposure_count": []}
    for u in range(n_users):
        first_exp = rng.integers(0, 15) if rng.random() > 0.3 else None
        count = 0
        for d in range(n_days):
            if rng.random() < 0.5:
                if first_exp is None:
                    first_exp = d
                count += 1
                since = d - first_exp if first_exp is not None else None
                p = base_rate + lift * np.exp(-since / half_life) if since is not None else base_rate
                outcome = int(rng.random() < p)
                rows["calendar"].append((d, outcome))
                if since is not None: rows["since_exposure"].append((since, outcome))
                if count > 0: rows["exposure_count"].append((count, outcome))

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.0), sharey=True)
    for ax, key, label in zip(axes, ["calendar", "since_exposure", "exposure_count"],
                               ["calendar day", "days since first exposure", "exposure count"]):
        data = np.array(rows[key])
        xs = sorted(set(data[:, 0].astype(int)))
        ys = [data[data[:, 0].astype(int) == x, 1].mean() for x in xs if len(data[data[:, 0].astype(int) == x]) > 10]
        xs = [x for x in xs if len(data[data[:, 0].astype(int) == x]) > 10]
        ax.plot(xs[:40], ys[:40], color=PALETTE["focus"], linewidth=1.5, alpha=0.8)
        ax.axhline(base_rate, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.set_xlabel(label)
        ax.set_ylim(0.10, 0.40)
        if ax is axes[0]: ax.set_ylabel("conversion rate")
    fig.suptitle("same event log, three different measurement axes, three different pictures of novelty decay")
    out = IMG_DIR / "three_measurement_schemes.png"
    fig.savefig(out); plt.close(fig); return out


def main():
    ensure_dirs()
    paths = [(render_novelty_lifecycle(), "derived", "Story Ch.14: novelty lifecycle curves"),
             (render_three_measurement_schemes(), 14, "Story Ch.14: three measurement schemes on same event log")]
    print(f"Story Ch.14: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
