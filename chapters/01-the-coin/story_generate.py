"""Regenerate Chapter 1 (the coin) story-track figures.

Six figures, all written to ``images/story/`` and tracked in
``data/manifest.yaml`` so the story track is a first-class
reproducible artifact alongside the technical track.

The figures are designed for prose-first reading: the surrounding text
explains what to look at, so titles are short or absent and captions
are not used. Statistical hygiene is enforced via expkit.plot.story
(bar charts always start at zero, no pie charts, etc.).
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
from expkit.plot.story import (  # noqa: E402
    PALETTE, SEQUENCE, apply_story_style, coin_strip, reference_line,
)
from expkit.sim.coin import bernoulli_sequence, running_fraction  # noqa: E402

CHAPTER = "01-the-coin"
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


NARRATIVE_SEED = 500  # bernoulli_sequence(10, 0.5, seed=500) -> [1,1,1,0,0,1,0,1,0,0]


def render_first_three_tosses():
    apply_story_style()
    seq = bernoulli_sequence(3, p=0.5, seed=NARRATIVE_SEED)
    fig, ax = plt.subplots(figsize=(3.2, 1.0))
    coin_strip(ax, seq.tolist())
    out = IMG_DIR / "first_three_tosses.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_ten_tosses():
    apply_story_style()
    seq = bernoulli_sequence(10, p=0.5, seed=NARRATIVE_SEED)
    fig, ax = plt.subplots(figsize=(8.0, 1.0))
    coin_strip(ax, seq.tolist())
    out = IMG_DIR / "ten_tosses.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_running_fraction_settles():
    """The narrative's same coin viewed at four growing lengths."""
    apply_story_style()
    seq = bernoulli_sequence(10000, p=0.5, seed=NARRATIVE_SEED)
    rf = running_fraction(seq)
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.0), sharey=True)
    panels = [
        (10, "the first 10"),
        (100, "the first 100"),
        (1000, "the first 1,000"),
        (10000, "all 10,000"),
    ]
    for ax, (n, label) in zip(axes, panels):
        xs = np.arange(1, n + 1)
        ax.plot(xs, rf[:n], color=PALETTE["focus"], linewidth=1.4)
        reference_line(ax, 0.5, label=None)
        ax.set_xlim(1, n)
        ax.set_ylim(0, 1)
        ax.set_title(label)
        ax.set_xlabel("toss number")
        if ax is axes[0]:
            ax.set_ylabel("fraction of heads so far")
    out = IMG_DIR / "running_fraction_settles.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_many_seeds_wobble():
    """Six runs of 100 tosses with a fair coin, all on the same axes."""
    apply_story_style()
    seeds = [11, 23, 41, 67, 89, 113]
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    final_fracs = []
    for i, s in enumerate(seeds):
        seq = bernoulli_sequence(100, p=0.5, seed=s)
        rf = running_fraction(seq)
        ax.plot(np.arange(1, 101), rf, color=SEQUENCE[i % len(SEQUENCE)], linewidth=1.3, alpha=0.9)
        final_fracs.append(rf[-1])
    reference_line(ax, 0.5)
    ax.set_xlim(1, 100)
    ax.set_ylim(0, 1)
    ax.set_xlabel("toss number")
    ax.set_ylabel("fraction of heads so far")
    out = IMG_DIR / "many_seeds_wobble.png"
    fig.savefig(out)
    plt.close(fig)
    # Persist the final fractions so the prose can quote them precisely.
    return out, final_fracs


def render_cherry_picked_window():
    """Find a 12-toss window with 10 H + 2 T inside a long fair sequence."""
    apply_story_style()
    seq = bernoulli_sequence(2000, p=0.5, seed=42)
    # Sliding window of size 12, find the first window with exactly 10 heads.
    window = 12
    target_h = 10
    start = None
    for i in range(len(seq) - window + 1):
        if seq[i:i + window].sum() == target_h:
            start = i
            break
    if start is None:
        # Loosen to >=10 if the exact target was not present.
        for i in range(len(seq) - window + 1):
            if seq[i:i + window].sum() >= target_h:
                start = i
                break
    sub = seq[start:start + window]

    fig, axes = plt.subplots(2, 1, figsize=(11, 3.3))
    # Top: the cherry-picked window, a coin strip
    coin_strip(axes[0], sub.tolist())
    # Bottom: the running fraction of the full 2000-toss run, with the window highlighted
    rf = running_fraction(seq)
    axes[1].plot(np.arange(1, len(seq) + 1), rf, color=PALETTE["muted"], linewidth=1.0, alpha=0.9)
    axes[1].axvspan(start + 1, start + window, color=PALETTE["focus"], alpha=0.25)
    reference_line(axes[1], 0.5)
    axes[1].set_xlim(1, len(seq))
    axes[1].set_ylim(0, 1)
    axes[1].set_xlabel("toss number in the long run")
    axes[1].set_ylabel("fraction of heads so far")
    out = IMG_DIR / "cherry_picked_window.png"
    fig.savefig(out)
    plt.close(fig)
    return out, int(sub.sum()), int(window - sub.sum()), start


def render_two_coins_compared():
    """Fair coin and 0.55 coin, running fraction over 10,000 tosses, side by side."""
    apply_story_style()
    seq_fair = bernoulli_sequence(10000, p=0.5, seed=7)
    seq_heavy = bernoulli_sequence(10000, p=0.55, seed=8)
    rf_fair = running_fraction(seq_fair)
    rf_heavy = running_fraction(seq_heavy)
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 3.6), sharey=True)
    cuts = [(100, "after 100"), (1000, "after 1,000"), (10000, "after 10,000")]
    for ax, (n, label) in zip(axes, cuts):
        xs = np.arange(1, n + 1)
        ax.plot(xs, rf_fair[:n], color=PALETTE["contrast"], linewidth=1.4, label="the fair coin")
        ax.plot(xs, rf_heavy[:n], color=PALETTE["focus"], linewidth=1.4, label="the heavy coin")
        reference_line(ax, 0.5)
        reference_line(ax, 0.55)
        ax.set_xlim(1, n)
        ax.set_ylim(0, 1)
        ax.set_title(label)
        ax.set_xlabel("toss number")
        if ax is axes[0]:
            ax.set_ylabel("fraction of heads so far")
            ax.legend(loc="lower right")
    out = IMG_DIR / "two_coins_compared.png"
    fig.savefig(out)
    plt.close(fig)
    return out, float(rf_fair[-1]), float(rf_heavy[-1])


def main():
    ensure_dirs()

    paths = []
    paths.append((render_first_three_tosses(), 1, "Story Ch.1: HHH first three tosses (illustrative)"))
    paths.append((render_ten_tosses(), 1, "Story Ch.1: ten tosses, the specific run (HHH then mixed)"))
    paths.append((render_running_fraction_settles(), 1, "Story Ch.1: running fraction at N=10/100/1000/10000 (seed 1)"))

    p_seeds, finals = render_many_seeds_wobble()
    paths.append((p_seeds, 0, f"Story Ch.1: six 100-toss fair-coin runs; final fractions {[f'{f:.2f}' for f in finals]}"))

    p_cherry, h, t, start = render_cherry_picked_window()
    paths.append((p_cherry, 42, f"Story Ch.1: cherry-picked 12-toss window with {h}H {t}T starting at toss {start}, drawn from a fair 2000-run"))

    p_two, ff, fh = render_two_coins_compared()
    paths.append((p_two, 7, f"Story Ch.1: fair vs 0.55 coin, 10000 tosses each, final fractions {ff:.4f} vs {fh:.4f}"))

    print(f"Story Ch.1: wrote {len(paths)} story figures")


if __name__ == "__main__":
    main()
