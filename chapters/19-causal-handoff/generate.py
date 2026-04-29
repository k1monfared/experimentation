"""Regenerate Chapter 19 (causal handoff) figures."""

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

CHAPTER = "19-causal-handoff"
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


def render_selection_bias():
    """Show the trap: in observational data, treated and untreated differ on baseline."""
    apply_style()
    rng = np.random.default_rng(190)
    n = 5000
    # User has a latent baseline propensity; treatment is more likely if propensity is high.
    propensity = rng.normal(0, 1, n)
    # Treatment assignment: probability sigmoid(propensity)
    treated = rng.random(n) < 1 / (1 + np.exp(-propensity))
    # True treatment effect = +0.3 on outcome
    outcome = propensity + 0.3 * treated + rng.normal(0, 0.5, n)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0))
    # Naive: just compare treated vs untreated
    axes[0].hist(outcome[~treated], bins=40, alpha=0.55, color=PALETTE["frequentist"], label=f"untreated mean = {outcome[~treated].mean():.2f}")
    axes[0].hist(outcome[treated], bins=40, alpha=0.55, color=PALETTE["bayesian"], label=f"treated mean = {outcome[treated].mean():.2f}")
    axes[0].set_xlabel("outcome")
    axes[0].set_title(f"Naive observational diff: {outcome[treated].mean()-outcome[~treated].mean():+.2f}")
    axes[0].legend(fontsize=8)

    # The truth (had we randomized): treatment effect would have been 0.3
    axes[1].hist(propensity[~treated], bins=40, alpha=0.55, color=PALETTE["frequentist"], label="untreated propensity")
    axes[1].hist(propensity[treated], bins=40, alpha=0.55, color=PALETTE["bayesian"], label="treated propensity")
    axes[1].set_xlabel("baseline propensity")
    axes[1].set_title("Treated and untreated differ on baseline -> selection bias")
    axes[1].legend(fontsize=8)

    fig.suptitle("Naive observational comparison overstates the effect (true effect = 0.30)")
    fig.tight_layout()
    out = IMG_DIR / "selection_bias.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_when_experiments_fail():
    apply_style()
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.axis("off")
    bullets = [
        ("Long horizons", "Need 5+ years of data to see the effect; can't randomize that long without contamination."),
        ("Ethics", "Cannot randomly deny patients a vaccine."),
        ("Network effects", "Treating user A changes user A's friends' behaviour. Independence assumption violated."),
        ("Observational data", "We have logs from 2 years ago; the people in those logs were not randomly assigned."),
        ("One-time events", "Policy changes, announcements, regime shifts. There is no untreated counterfactual."),
    ]
    for i, (title, body) in enumerate(bullets):
        ax.text(0.0, 1 - i * 0.18, f"-> {title}", fontsize=12, weight="bold")
        ax.text(0.05, 1 - i * 0.18 - 0.06, body, fontsize=10, style="italic", wrap=True)
    ax.set_title("When experiments aren't enough")
    fig.tight_layout()
    out = IMG_DIR / "when_experiments_fail.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_selection_bias(),
        render_when_experiments_fail(),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 19 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 19: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
