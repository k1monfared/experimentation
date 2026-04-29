"""Regenerate Chapter 17 (attribution) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.attribution.touch import aggregate_credit  # noqa: E402
from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402

CHAPTER = "17-attribution"
CHAPTER_DIR = Path(__file__).resolve().parent
DATA_DIR = CHAPTER_DIR / "data"
IMG_DIR = CHAPTER_DIR / "images"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.yaml"


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
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
    m["artifacts"].append({"path": rel, "chapter": CHAPTER, "kind": kind, "seed": seed, "sha256": sha256, "description": description})


CHANNELS = ["search", "social", "email", "display", "direct"]


def simulate_journeys(n_users: int, seed: int = 0):
    """Simulate user journeys with channel touches and a conversion outcome."""
    rng = np.random.default_rng(seed)
    journeys = []
    # True channel coefficients (weights toward conversion)
    true_coef = {"search": 0.10, "social": 0.04, "email": 0.05, "display": 0.02, "direct": 0.20}
    for _ in range(n_users):
        n_touches = rng.integers(1, 6)
        touches = list(rng.choice(CHANNELS, size=n_touches, replace=True))
        times = sorted(rng.uniform(0, 30, size=n_touches).tolist())
        # Conversion probability is logistic in the sum of true_coef
        score = sum(true_coef[t] for t in touches)
        p = 1 / (1 + np.exp(-(score - 0.5)))
        converted = int(rng.random() < p)
        journeys.append((touches, times, converted))
    return journeys, true_coef


def render_attribution_comparison(manifest):
    apply_style()
    journeys, true_coef = simulate_journeys(20000, seed=170)
    schemes = ["first", "last", "linear", "time_decay"]
    results = {scheme: aggregate_credit(journeys, scheme=scheme) for scheme in schemes}

    df_true = pd.DataFrame({"channel": list(true_coef.keys()), "true_coef": list(true_coef.values())})
    df_true["true_share"] = df_true["true_coef"] / df_true["true_coef"].sum()

    fig, ax = plt.subplots(figsize=(11, 4.5))
    width = 0.18
    xs = np.arange(len(CHANNELS))
    cmap = plt.get_cmap("viridis")
    for i, (scheme, df) in enumerate(results.items()):
        df = df.set_index("channel").reindex(CHANNELS).reset_index()
        share = df["credit"] / df["credit"].sum()
        ax.bar(xs + (i - 1.5) * width, share, width=width, color=cmap(i / max(1, len(schemes) - 1)), label=scheme)
    ax.scatter(xs, df_true["true_share"], color=PALETTE["highlight"], s=80, zorder=5, label="true share")
    ax.set_xticks(xs)
    ax.set_xticklabels(CHANNELS)
    ax.set_ylabel("share of attributed credit")
    ax.set_title("Loop A: four schemes assign different shares to the same channels")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "scheme_comparison.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_treatment_lift_misallocation():
    """Boost touch #3 in every journey. Which scheme catches that it was channel-neutral?"""
    apply_style()
    rng = np.random.default_rng(1)
    n = 10000
    schemes = ["first", "last", "linear", "time_decay"]
    journeys_control = []
    journeys_treat = []
    for _ in range(n):
        n_touches = 4
        touches = list(rng.choice(CHANNELS, size=n_touches, replace=True))
        times = sorted(rng.uniform(0, 30, size=n_touches).tolist())
        # Control: conversion probability comes from sum of touches.
        score = 0.05 * n_touches + 0.05 * sum(t == "direct" for t in touches)
        p_c = 1 / (1 + np.exp(-(score - 0.5)))
        # Treatment: a +0.1 bump only when there's a 3rd touch, regardless of channel.
        p_t = 1 / (1 + np.exp(-(score - 0.5 + 0.1)))
        journeys_control.append((touches, times, int(rng.random() < p_c)))
        journeys_treat.append((touches, times, int(rng.random() < p_t)))
    fig, ax = plt.subplots()
    width = 0.2
    xs = np.arange(len(schemes))
    cmap = plt.get_cmap("viridis")
    for i, scheme in enumerate(schemes):
        cred_c = aggregate_credit(journeys_control, scheme=scheme).set_index("channel").reindex(CHANNELS)
        cred_t = aggregate_credit(journeys_treat, scheme=scheme).set_index("channel").reindex(CHANNELS)
        # Credit lift across all channels (a balanced treatment should lift them all equally)
        lifts = (cred_t["credit"] - cred_c["credit"]) / cred_c["credit"].clip(lower=1)
        ax.bar(np.arange(len(CHANNELS)) + (i - 1.5) * width, lifts, width=width, color=cmap(i / max(1, len(schemes) - 1)), label=scheme)
    ax.set_xticks(np.arange(len(CHANNELS)))
    ax.set_xticklabels(CHANNELS)
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_ylabel("relative credit lift (treatment vs control)")
    ax.set_title("Loop B: treatment uniformly bumps conversions. Schemes mis-allocate the lift.")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "treatment_misallocation.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_attribution_comparison(manifest),
        render_treatment_lift_misallocation(),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 17 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 17: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
