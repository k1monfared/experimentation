"""Regenerate Chapter 10 figures: clickbait curves, aggregates hide cohorts, guardrail multiplicity."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.plot.story import PALETTE, apply_story_style, reference_line  # noqa: E402

CHAPTER = "10-industry-experimentation"
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


def render_clickbait_curves():
    apply_story_style()
    days = np.arange(1, 31)
    click_lift = 10 * np.exp(-days / 7)  # decays from +10% to ~0
    retention_loss = -5 * (1 - np.exp(-(days - 1) / 12))  # builds from 0 to -5pp
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(days, click_lift, color=PALETTE["focus"], linewidth=2, label="click lift (%)")
    ax.plot(days, retention_loss, color="#9a6f9c", linewidth=2, label="retention change (pp)")
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.axvline(7, color=PALETTE["ink"], linestyle=":", linewidth=1, label="typical experiment ends")
    ax.set_xlabel("days since launch")
    ax.set_ylabel("effect")
    ax.set_title("clicks rise then fade; retention damage builds slowly")
    ax.legend()
    out = IMG_DIR / "clickbait_curves.png"
    fig.savefig(out); plt.close(fig); return out


def render_aggregate_hides_cohorts():
    apply_story_style()
    cohorts = ["most engaged 10%", "moderate 30%", "long tail 60%"]
    lifts = [-2, 3, 6]
    weights = [0.10, 0.30, 0.60]
    aggregate = sum(l * w for l, w in zip(lifts, weights))
    fig, ax = plt.subplots(figsize=(11, 4.5))
    colors = ["#9a6f9c", PALETTE["contrast"], PALETTE["focus"]]
    bars = ax.bar(cohorts, lifts, color=colors, width=0.65)
    for b, l in zip(bars, lifts):
        ax.text(b.get_x() + b.get_width() / 2, l + (0.2 if l > 0 else -0.5),
                f"{l:+.1f}%", ha="center", fontsize=11)
    ax.axhline(aggregate, color=PALETTE["ink"], linestyle="--", linewidth=1.5,
               label=f"aggregate (+{aggregate:.1f}%)")
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_ylabel("click-rate lift (%)")
    ax.set_ylim(-4, 8)
    ax.legend(loc="upper left")
    ax.set_title("aggregate is positive. Most-engaged cohort regressed.")
    out = IMG_DIR / "aggregate_hides_cohorts.png"
    fig.savefig(out); plt.close(fig); return out


def render_guardrail_multiplicity():
    apply_story_style()
    rng = np.random.default_rng(0)
    n_metrics_list = [1, 5, 10, 20, 50, 100]
    n_trials = 5000
    naive_rates = []
    bonf_rates = []
    for k in n_metrics_list:
        any_naive = 0
        any_bonf = 0
        for _ in range(n_trials):
            ps = rng.uniform(0, 1, size=k)
            if np.any(ps < 0.05): any_naive += 1
            if np.any(ps < 0.05 / k): any_bonf += 1
        naive_rates.append(any_naive / n_trials)
        bonf_rates.append(any_bonf / n_trials)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(n_metrics_list, naive_rates, "o-", color=PALETTE["focus"],
            linewidth=2, label="no correction (naive)")
    ax.plot(n_metrics_list, bonf_rates, "s-", color=PALETTE["contrast"],
            linewidth=2, label="Bonferroni correction")
    ax.axhline(0.05, color=PALETTE["muted"], linestyle="--", linewidth=1, label="promised 5%")
    ax.set_xscale("log")
    ax.set_xlabel("number of guardrail metrics (log scale)")
    ax.set_ylabel("fraction of runs where at least one falsely fires")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="center right")
    ax.set_title("with 20 metrics, naive checking blows past 50% false alarms")
    out = IMG_DIR / "guardrail_multiplicity.png"
    fig.savefig(out); plt.close(fig); return out


def main():
    ensure_dirs()
    paths = []
    paths.append((render_clickbait_curves(), "derived",
                  "Story Ch.10: clickbait click lift vs retention loss curves"))
    paths.append((render_aggregate_hides_cohorts(), "derived",
                  "Story Ch.10: aggregate hides cohort-level pattern"))
    paths.append((render_guardrail_multiplicity(), 0,
                  "Story Ch.10: guardrail false-alarm rate as metric count grows"))
    print(f"Story Ch.10: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
