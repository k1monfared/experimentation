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
from expkit.io.samples import _sha256_file, save_idata  # noqa: E402
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


def render_bayesian_attribution(manifest):
    """Bayesian multi-touch attribution: logistic regression with channel coefficients.

    Each user's conversion probability is sigmoid(intercept + sum_c coef[c] * count[c]).
    Posterior over the per-channel coefficients tells us each channel's marginal
    contribution to conversion -- the model-based answer to "who deserves credit?".
    """
    import pymc as pm

    apply_style()
    journeys, true_coef = simulate_journeys(20000, seed=170)

    # Build the design matrix: one row per journey, one column per channel,
    # entry = number of times that channel was touched.
    counts = np.zeros((len(journeys), len(CHANNELS)), dtype=int)
    converted = np.zeros(len(journeys), dtype=int)
    for i, (touches, _, conv) in enumerate(journeys):
        for ch in touches:
            counts[i, CHANNELS.index(ch)] += 1
        converted[i] = conv

    coords = {"channel": CHANNELS}
    with pm.Model(coords=coords):
        intercept = pm.Normal("intercept", mu=-0.5, sigma=1.0)
        coef = pm.Normal("coef", mu=0.0, sigma=0.5, dims="channel")
        logit_p = intercept + pm.math.dot(counts, coef)
        pm.Bernoulli("y", logit_p=logit_p, observed=converted)
        idata = pm.sample(
            draws=1500, chains=2, tune=1500, random_seed=1717,
            progressbar=False, return_inferencedata=True, target_accept=0.95,
        )
    res = save_idata(idata, DATA_DIR / "bayesian_attribution", seed=1717, meta={
        "channels": CHANNELS,
        "true_coef": true_coef,
        "n_users": len(journeys),
        "model": "logistic regression: P(convert) = sigmoid(intercept + sum_c coef[c] * count[c])",
    })
    add_artifact(manifest, path=res.path, kind="idata", seed=1717, sha256=res.sha256, description="Bayesian multi-touch attribution model posterior")

    posterior_means = idata.posterior["coef"].mean(dim=("chain", "draw")).values
    lo = idata.posterior["coef"].quantile(0.025, dim=("chain", "draw")).values
    hi = idata.posterior["coef"].quantile(0.975, dim=("chain", "draw")).values
    true_vec = np.array([true_coef[ch] for ch in CHANNELS])

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    cmap = plt.get_cmap("viridis")
    xs = np.arange(len(CHANNELS))
    # Left: posterior coefficients vs truth
    for i, ch in enumerate(CHANNELS):
        axes[0].errorbar(i, posterior_means[i], yerr=[[posterior_means[i] - lo[i]], [hi[i] - posterior_means[i]]],
                         fmt="o", color=cmap(i / max(1, len(CHANNELS) - 1)), capsize=4, markersize=8,
                         label="Bayesian posterior 95% CI" if i == 0 else None)
    axes[0].scatter(xs, true_vec, color=PALETTE["highlight"], marker="s", s=80, zorder=5, label="true coefficient")
    axes[0].axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[0].set_xticks(xs); axes[0].set_xticklabels(CHANNELS)
    axes[0].set_ylabel("logit-scale coefficient")
    axes[0].set_title("Loop C: posterior over channel coefficients (recovers truth)")
    axes[0].legend(fontsize=8)
    # Right: heuristic share comparison vs Bayesian normalized share
    schemes = ["first", "last", "linear", "time_decay"]
    width = 0.18
    bayes_share = np.maximum(posterior_means, 0); bayes_share = bayes_share / bayes_share.sum()
    true_share = true_vec / true_vec.sum()
    for i, sch in enumerate(schemes):
        df = aggregate_credit(journeys, scheme=sch).set_index("channel").reindex(CHANNELS)
        share = df["credit"] / df["credit"].sum()
        axes[1].bar(xs + (i - 2) * width, share, width=width, color=cmap(i / max(1, len(schemes) - 1)), label=sch, alpha=0.6)
    axes[1].bar(xs + 2 * width, bayes_share, width=width, color=PALETTE["bayesian"], label="Bayesian (normalized coef)")
    axes[1].scatter(xs, true_share, color=PALETTE["highlight"], marker="s", s=80, zorder=5, label="true share")
    axes[1].set_xticks(xs); axes[1].set_xticklabels(CHANNELS)
    axes[1].set_ylabel("attributed share")
    axes[1].set_title("Loop D: heuristic shares vs Bayesian-derived shares")
    axes[1].legend(fontsize=7, ncols=2)
    fig.tight_layout()
    out = IMG_DIR / "bayesian_attribution.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_attribution_comparison(manifest),
        render_treatment_lift_misallocation(),
        render_bayesian_attribution(manifest),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 17 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 17: wrote {len(paths)} figures + 1 PyMC trace")


if __name__ == "__main__":
    main()
