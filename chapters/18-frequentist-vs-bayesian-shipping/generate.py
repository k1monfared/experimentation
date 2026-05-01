"""Regenerate Chapter 18 (F-vs-B shipping capstone) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.inference.normal import two_proportion_z  # noqa: E402
from expkit.io.samples import _sha256_file, save_samples  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.sim.abtest import two_arm_binary  # noqa: E402

CHAPTER = "18-frequentist-vs-bayesian-shipping"
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


def run_simulator(n_runs: int, n_per_arm: int, mmu: float = 0.005, seed: int = 0) -> pd.DataFrame:
    """Run n_runs synthetic A/B tests with effects drawn from a population.

    Records frequentist decisions (one rule "in the wild" without an MMU gate, one
    "matched" rule with a point-estimate MMU gate) and the Bayesian decision
    (P(diff > MMU) > 0.95) along with the true effect.

    Population caveat: true_diff is drawn from Normal(0, 0.01). About 38% of mass
    lies within +/- MMU and ~95% within +/- 0.02, which drives the murky-middle
    framing. Different effect populations (heavy-tailed, skewed positive, mixture
    of zeros plus a discrete spike) would shift the cost trade-offs.
    """
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n_runs):
        true_diff = float(rng.normal(0, 0.01))  # mean zero, std 1pp
        pc = 0.10
        pt = pc + true_diff
        if pt < 0.001 or pt > 0.999:
            continue
        exp = two_arm_binary(n_per_arm, pc, pt, seed=int(rng.integers(0, 2**30)))
        z = two_proportion_z(int(exp.treatment.sum()), n_per_arm, int(exp.control.sum()), n_per_arm)
        f_ship = (z.p_value < 0.05) and (z.point_estimate > 0)
        # Matched frequentist rule: p < 0.05 AND point estimate > MMU (not just > 0).
        # Lets the reader separate "lens effect" from "with-MMU vs without-MMU effect".
        f_ship_matched = (z.p_value < 0.05) and (z.point_estimate > mmu)
        # Bayesian: posterior P(diff > MMU) > 0.95 via Beta-Binomial conjugate.
        a_c, b_c = 1 + int(exp.control.sum()), 1 + (n_per_arm - int(exp.control.sum()))
        a_t, b_t = 1 + int(exp.treatment.sum()), 1 + (n_per_arm - int(exp.treatment.sum()))
        # Bug fix: previously local rng was reseeded to 0 every iteration, which
        # correlated the Monte-Carlo noise across all runs. Spawn a per-run rng
        # from the outer rng instead so each posterior draw is independent.
        local = np.random.default_rng(rng.integers(0, 2**30))
        diffs = local.beta(a_t, b_t, 4000) - local.beta(a_c, b_c, 4000)
        b_ship = (diffs > mmu).mean() > 0.95
        rows.append({
            "true_diff": true_diff,
            "f_ship": f_ship,
            "f_ship_matched": f_ship_matched,
            "b_ship": b_ship,
            "obs_diff": z.point_estimate,
            "p": z.p_value,
        })
    return pd.DataFrame(rows)


def render_confusion_matrix(df: pd.DataFrame) -> Path:
    apply_style()
    matrix = df.groupby(["f_ship", "b_ship"]).size().unstack(fill_value=0)
    matrix = matrix.reindex(index=[False, True], columns=[False, True], fill_value=0)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.imshow(matrix.values, cmap="viridis", aspect="auto")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(int(matrix.values[i, j])), ha="center", va="center", color="white", fontsize=14)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["B no-ship", "B ship"])
    ax.set_yticklabels(["F no-ship", "F ship"])
    ax.set_title("Loop B: confusion matrix of frequentist vs Bayesian decisions")
    fig.tight_layout()
    out = IMG_DIR / "confusion_matrix.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_decision_by_truth(df: pd.DataFrame) -> Path:
    apply_style()
    bins = np.linspace(df["true_diff"].min(), df["true_diff"].max(), 16)
    df["bin"] = pd.cut(df["true_diff"], bins=bins, include_lowest=True)
    f_ship_rate = df.groupby("bin", observed=True)["f_ship"].mean()
    b_ship_rate = df.groupby("bin", observed=True)["b_ship"].mean()
    centers = [(b.left + b.right) / 2 for b in f_ship_rate.index]
    fig, ax = plt.subplots()
    ax.plot(centers, f_ship_rate.values, color=PALETTE["frequentist"], label="frequentist ship rate")
    ax.plot(centers, b_ship_rate.values, color=PALETTE["bayesian"], label="Bayesian ship rate (MMU=0.005)")
    ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1, label="no effect")
    ax.axvline(0.005, color=PALETTE["highlight"], linestyle=":", linewidth=1, label="MMU")
    ax.set_xlabel("true effect")
    ax.set_ylabel("ship rate")
    ax.set_title("Loop A: ship rate vs true effect, both lenses")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "ship_by_truth.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_cost_analysis(df: pd.DataFrame) -> Path:
    """Per-decision expected cost. False-positive ship costs C1; missed-win costs C2."""
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0))
    for ax, c2 in zip(axes, [1.0, 5.0]):
        c1 = 1.0
        # FP ship: f_ship=True or b_ship=True with true_diff <= 0 (we shipped a non-improvement)
        # Missed win: f_ship=False or b_ship=False with true_diff > MMU (failed to ship a real improvement)
        mmu = 0.005
        f_fp_rate = ((df["f_ship"] == True) & (df["true_diff"] <= 0)).mean()
        f_miss_rate = ((df["f_ship"] == False) & (df["true_diff"] > mmu)).mean()
        b_fp_rate = ((df["b_ship"] == True) & (df["true_diff"] <= 0)).mean()
        b_miss_rate = ((df["b_ship"] == False) & (df["true_diff"] > mmu)).mean()
        ax.bar(["F", "B"], [c1 * f_fp_rate + c2 * f_miss_rate, c1 * b_fp_rate + c2 * b_miss_rate], color=[PALETTE["frequentist"], PALETTE["bayesian"]])
        ax.set_ylabel("expected cost per decision")
        ax.set_title(f"FP cost = {c1}, miss cost = {c2}")
    fig.suptitle("Loop C: expected cost depends on the FP-vs-miss weighting")
    fig.tight_layout()
    out = IMG_DIR / "cost_analysis.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_joint_decision(df: pd.DataFrame) -> Path:
    """Joint rule: ship only if both lenses agree."""
    apply_style()
    df = df.copy()
    df["joint_ship"] = df["f_ship"] & df["b_ship"]
    bins = np.linspace(df["true_diff"].min(), df["true_diff"].max(), 16)
    df["bin"] = pd.cut(df["true_diff"], bins=bins, include_lowest=True)
    rates = df.groupby("bin", observed=True)[["f_ship", "b_ship", "joint_ship"]].mean()
    centers = [(b.left + b.right) / 2 for b in rates.index]
    fig, ax = plt.subplots()
    ax.plot(centers, rates["f_ship"], color=PALETTE["frequentist"], label="frequentist alone")
    ax.plot(centers, rates["b_ship"], color=PALETTE["bayesian"], label="Bayesian alone")
    ax.plot(centers, rates["joint_ship"], color=PALETTE["highlight"], label="both must agree")
    ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.axvline(0.005, color=PALETTE["muted"], linestyle=":", linewidth=1, label="MMU")
    ax.set_xlabel("true effect")
    ax.set_ylabel("ship rate")
    ax.set_title("Loop E: joint rule is more conservative than either lens alone")
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = IMG_DIR / "joint_decision.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    df = run_simulator(n_runs=2000, n_per_arm=2000, mmu=0.005, seed=180)
    csv_path = DATA_DIR / "ship_decisions.csv"
    df.to_csv(csv_path, index=False)
    add_artifact(manifest, path=csv_path, kind="samples", seed=180, sha256=_sha256_file(csv_path), description="Loop A-E: 2,000 simulated A/B tests with frequentist + Bayesian decisions")

    paths = [
        render_decision_by_truth(df),
        render_confusion_matrix(df),
        render_cost_analysis(df),
        render_joint_decision(df),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 18 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 18: wrote {len(paths)} figures + 1 dataset")


if __name__ == "__main__":
    main()
