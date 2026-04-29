"""Regenerate Chapter 9 (wine and the small print) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.sim.user_segments import SegmentSpec, segmented_binary  # noqa: E402

CHAPTER = "09-wine-and-the-small-print"
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


def render_external_validity():
    """The study only sampled one segment, but the conclusion is generalized to all."""
    apply_style()
    studied = SegmentSpec("22yo college students", fraction=1.0, baseline=0.40, treatment_lift=0.05)
    universe = [
        SegmentSpec("22yo college students", 0.10, 0.40, 0.05),
        SegmentSpec("40yo under stress", 0.20, 0.55, -0.02),
        SegmentSpec("65+ healthy adults", 0.20, 0.30, 0.01),
        SegmentSpec("pregnant women", 0.05, 0.45, -0.10),
        SegmentSpec("teens", 0.10, 0.20, -0.05),
        SegmentSpec("middle-aged sedentary", 0.35, 0.50, 0.00),
    ]
    studied_only = segmented_binary(2000, [studied], seed=900)
    universe_pop = segmented_binary(20000, universe, seed=901)

    studied_diff = studied_only["22yo college students"]["treatment"].mean() - studied_only["22yo college students"]["control"].mean()
    universe_diff_each = {s.name: universe_pop[s.name]["treatment"].mean() - universe_pop[s.name]["control"].mean() for s in universe}

    fig, ax = plt.subplots(figsize=(11, 4.0))
    names = ["studied: 22yo college\nN = 2000"] + [f"{s.name}\nN = {int(20000 * s.fraction)}" for s in universe]
    diffs = [studied_diff] + [universe_diff_each[s.name] for s in universe]
    cmap = plt.get_cmap("viridis")
    bars = ax.bar(names, diffs, color=[cmap(0.0)] + [cmap(0.4 + 0.6 * i / max(1, len(universe) - 1)) for i in range(len(universe))])
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.axhline(studied_diff, color=PALETTE["bayesian"], linestyle=":", linewidth=1, label=f"headline result from study ({studied_diff:+.3f})")
    for b, d in zip(bars, diffs):
        ax.text(b.get_x() + b.get_width() / 2, d + 0.005, f"{d:+.3f}", ha="center", fontsize=8)
    ax.set_ylabel("treatment - control on outcome")
    ax.set_title("Loop A: study sampled '22yo college'. Headline +5pp. The other groups disagree.")
    ax.legend()
    plt.setp(ax.get_xticklabels(), fontsize=8, rotation=10)
    fig.tight_layout()
    out = IMG_DIR / "external_validity.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_outcome_choice():
    """The same effect on a narrow proxy can be invisible (or reversed) on the metric we actually care about."""
    apply_style()
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    metrics = ["resting heart rate (-3%)", "exercise tolerance (+1%)", "all-cause mortality (-0.2%)"]
    effect_sizes = [-0.03, 0.01, -0.002]
    cis = [(-0.05, -0.01), (-0.01, 0.03), (-0.01, 0.006)]
    cmap = plt.get_cmap("viridis")
    for i, (m, eff, ci) in enumerate(zip(metrics, effect_sizes, cis)):
        ax.errorbar(eff, i, xerr=[[eff - ci[0]], [ci[1] - eff]], fmt="o", color=cmap(i / max(1, len(metrics) - 1)), capsize=4)
    ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_yticks(range(len(metrics)))
    ax.set_yticklabels(metrics)
    ax.set_xlabel("effect with 95% CI")
    ax.set_title("Loop B: 'good' depends on which outcome you measure")
    fig.tight_layout()
    out = IMG_DIR / "outcome_choice.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_side_effects():
    apply_style()
    metrics = ["target metric", "secondary 1", "secondary 2 (harm)"]
    rng = np.random.default_rng(0)
    n = 1500
    # Treatment helps target, neutral on secondary 1, hurts secondary 2.
    target_c = rng.normal(0, 1, n)
    target_t = rng.normal(0.3, 1, n)
    sec1_c = rng.normal(0, 1, n)
    sec1_t = rng.normal(0.0, 1, n)
    harm_c = rng.normal(0, 1, n)
    harm_t = rng.normal(-0.4, 1, n)
    fig, ax = plt.subplots(figsize=(8.5, 4.0))
    diffs = [target_t.mean() - target_c.mean(), sec1_t.mean() - sec1_c.mean(), harm_t.mean() - harm_c.mean()]
    cis = []
    for c, t in [(target_c, target_t), (sec1_c, sec1_t), (harm_c, harm_t)]:
        se = np.sqrt(c.var(ddof=1) / n + t.var(ddof=1) / n)
        d = t.mean() - c.mean()
        cis.append((d - 1.96 * se, d + 1.96 * se))
    cmap = plt.get_cmap("viridis")
    for i, (m, d, ci) in enumerate(zip(metrics, diffs, cis)):
        ax.errorbar(d, i, xerr=[[d - ci[0]], [ci[1] - d]], fmt="o", color=cmap(i / max(1, len(metrics) - 1)), capsize=4)
    ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_yticks(range(len(metrics)))
    ax.set_yticklabels(metrics)
    ax.set_xlabel("effect with 95% CI")
    ax.set_title("Loop C: side effects -- the same intervention helps and hurts depending on which outcome we measure")
    fig.tight_layout()
    out = IMG_DIR / "side_effects.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_tradeoff():
    """Tradeoff knob: weight target vs harm and watch the ship/no-ship boundary move."""
    apply_style()
    target_effect = 0.30
    harm_effect = -0.40
    weights_target = np.linspace(0, 1, 100)
    utility = weights_target * target_effect + (1 - weights_target) * harm_effect
    fig, ax = plt.subplots()
    ax.plot(weights_target, utility, color=PALETTE["frequentist"])
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    crossing_idx = np.where(np.diff(np.sign(utility)))[0]
    if len(crossing_idx):
        ax.axvline(weights_target[crossing_idx[0]], color=PALETTE["highlight"], linestyle=":", linewidth=1, label=f"ship/no-ship boundary at weight {weights_target[crossing_idx[0]]:.2f}")
    ax.set_xlabel("weight on target metric (vs harm metric)")
    ax.set_ylabel("expected utility")
    ax.set_title("Loop D: same data, different stakeholder weights -> different decisions")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "tradeoff.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_external_validity(),
        render_outcome_choice(),
        render_side_effects(),
        render_tradeoff(),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 9 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 9: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
