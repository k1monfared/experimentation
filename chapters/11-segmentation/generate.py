"""Regenerate Chapter 11 (segmentation done right) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.segments.behavioral import simulate_population, BEHAVIORAL_LABELS  # noqa: E402

CHAPTER = "11-segmentation"
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


def render_demographic_vs_behavioral(manifest):
    """Same population. Slice by demographics (no signal) vs behavioural (huge differences)."""
    apply_style()
    rng = np.random.default_rng(110)
    n = 5000
    df = simulate_population(n, seed=110)
    # Add a fake demographic that we'll show is uninformative.
    df["country"] = rng.choice(["A", "B", "C"], size=n)
    df["age"] = rng.integers(18, 65, size=n)
    # Treatment effect is heterogeneous by behavioural segment, NOT by demographics.
    treatment_lift_by_segment = {"active_contributor": 0.10, "active_consumer": 0.04, "silent_intentional": -0.03, "passive_consumer": 0.0}
    df["arm"] = rng.choice(["control", "treatment"], size=n)
    base_p = 0.30
    df["outcome"] = 0
    for seg, lift in treatment_lift_by_segment.items():
        for arm in ["control", "treatment"]:
            mask = (df["segment"] == seg) & (df["arm"] == arm)
            p = base_p + (lift if arm == "treatment" else 0.0)
            df.loc[mask, "outcome"] = rng.binomial(1, max(0, min(1, p)), size=int(mask.sum()))

    # Demographic slice: by country
    by_country = df.groupby(["country", "arm"])["outcome"].mean().unstack()
    country_lifts = by_country["treatment"] - by_country["control"]
    # Behavioural slice
    by_segment = df.groupby(["segment", "arm"])["outcome"].mean().unstack()
    segment_lifts = by_segment["treatment"] - by_segment["control"]
    # Aggregate
    pooled = df.groupby("arm")["outcome"].mean()
    pooled_lift = pooled["treatment"] - pooled["control"]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0), sharey=True)
    cmap = plt.get_cmap("viridis")
    axes[0].bar(country_lifts.index, country_lifts.values, color=[cmap(i / max(1, len(country_lifts) - 1)) for i in range(len(country_lifts))])
    axes[0].axhline(pooled_lift, color=PALETTE["bayesian"], linestyle=":", linewidth=1, label=f"pooled lift = {pooled_lift:+.3f}")
    axes[0].axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[0].set_title("By demographic slice (country)")
    axes[0].set_ylabel("treatment - control")
    axes[0].legend()
    axes[1].bar(segment_lifts.index, segment_lifts.values, color=[cmap(i / max(1, len(segment_lifts) - 1)) for i in range(len(segment_lifts))])
    axes[1].axhline(pooled_lift, color=PALETTE["bayesian"], linestyle=":", linewidth=1, label=f"pooled lift = {pooled_lift:+.3f}")
    axes[1].axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[1].set_title("By behavioural segment")
    axes[1].legend()
    plt.setp(axes[1].get_xticklabels(), rotation=15, fontsize=8)
    fig.suptitle("Loop A: demographic slicing is flat. Behavioural slicing reveals hetero effects.")
    fig.tight_layout()
    out = IMG_DIR / "demographic_vs_behavioral.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_segment_signature():
    """Show the three behavioural axes for each segment."""
    apply_style()
    df = simulate_population(5000, seed=111)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5), sharey=False)
    for ax, col in zip(axes, ["weekly_active_rate", "contribution_rate", "intentional_rate"]):
        for label in BEHAVIORAL_LABELS:
            sub = df[df["segment"] == label][col]
            ax.hist(sub, bins=30, alpha=0.5, label=label)
        ax.set_xlabel(col)
        ax.legend(fontsize=7)
    fig.suptitle("Loop B: each behavioural segment has a distinctive signature on the three axes")
    fig.tight_layout()
    out = IMG_DIR / "segment_signature.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_segmentation_choices():
    """Three different segmentation schemes on the same population, showing they tell different stories."""
    apply_style()
    rng = np.random.default_rng(112)
    n = 4000
    df = simulate_population(n, seed=112)
    # Three segmentation schemes:
    # 1. Tenure (synthetic, simple) -- recently joined vs veteran
    df["tenure_days"] = rng.integers(0, 800, size=n)
    df["tenure_seg"] = np.where(df["tenure_days"] < 90, "new", "veteran")
    # 2. Activity tertile
    df["activity_seg"] = pd.qcut(df["weekly_active_rate"], q=3, labels=["low_active", "med_active", "high_active"])
    # 3. Behavioural label (already defined)
    # Apply a treatment that helps high-active, hurts low-active, neutral middle.
    df["arm"] = rng.choice(["control", "treatment"], size=n)
    base_p = 0.20
    df["outcome"] = rng.binomial(1, base_p, n)
    # Inject heterogeneity tied to weekly_active_rate
    treat_mask = df["arm"] == "treatment"
    new_p = np.clip(base_p + (df.loc[treat_mask, "weekly_active_rate"] - 0.4) * 0.3, 0.0, 1.0)
    df.loc[treat_mask, "outcome"] = rng.binomial(1, new_p)

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
    for ax, scheme, title in zip(
        axes,
        ["tenure_seg", "activity_seg", "segment"],
        ["Tenure (new vs veteran)", "Activity tertile", "Behavioural label"],
    ):
        diffs = df.groupby([scheme, "arm"])["outcome"].mean().unstack()
        lifts = diffs["treatment"] - diffs["control"]
        ax.bar(lifts.index.astype(str), lifts.values, color=plt.get_cmap("viridis")(np.linspace(0, 1, len(lifts))))
        ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.set_title(title)
        ax.set_ylabel("lift")
        plt.setp(ax.get_xticklabels(), rotation=15, fontsize=8)
    fig.suptitle("Loop C: same data, three segmentation schemes, three stories")
    fig.tight_layout()
    out = IMG_DIR / "segmentation_choices.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_demographic_vs_behavioral(manifest),
        render_segment_signature(),
        render_segmentation_choices(),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 11 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 11: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
