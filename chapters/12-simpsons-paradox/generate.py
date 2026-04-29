"""Regenerate Chapter 12 (Simpson's paradox) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file, save_samples  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.sim.user_segments import SegmentSpec, imbalanced_assignment  # noqa: E402

CHAPTER = "12-simpsons-paradox"
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


def render_paradox_construction():
    """Two segments, both helped by treatment. But aggregate shows treatment losing, because of unbalanced assignment."""
    apply_style()
    specs = [
        SegmentSpec("segment A (small, high baseline)", 0.20, 0.80, 0.05),
        SegmentSpec("segment B (large, low baseline)", 0.80, 0.20, 0.05),
    ]
    # Imbalanced assignment: treatment over-represented in low-baseline segment B.
    treatment_share = {"segment A (small, high baseline)": 0.20, "segment B (large, low baseline)": 0.80}
    pop = imbalanced_assignment(20000, specs, treatment_share, seed=1200)

    diffs_per_segment = {}
    for s in specs:
        c = pop[s.name]["control"].mean()
        t = pop[s.name]["treatment"].mean()
        diffs_per_segment[s.name] = (c, t, t - c, len(pop[s.name]["control"]) + len(pop[s.name]["treatment"]))

    # Pooled aggregate
    c_total = np.concatenate([pop[s.name]["control"] for s in specs])
    t_total = np.concatenate([pop[s.name]["treatment"] for s in specs])

    fig, ax = plt.subplots(figsize=(11, 4.0))
    cmap = plt.get_cmap("viridis")
    names = [s.name for s in specs] + ["pooled"]
    diffs = [diffs_per_segment[s.name][2] for s in specs] + [t_total.mean() - c_total.mean()]
    bars = ax.bar(names, diffs, color=[cmap(0.2), cmap(0.6), cmap(1.0)])
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    for b, d in zip(bars, diffs):
        ax.text(b.get_x() + b.get_width() / 2, d + (0.005 if d > 0 else -0.015), f"{d:+.3f}", ha="center", fontsize=10)
    ax.set_ylabel("treatment - control")
    ax.set_title("Loop A: each segment up by +0.05. Aggregate is negative because assignment was imbalanced.")
    plt.setp(ax.get_xticklabels(), fontsize=8, rotation=10)
    fig.tight_layout()
    out = IMG_DIR / "paradox_construction.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_when_does_it_flip(manifest):
    """Sweep: vary the treatment share in segment A while holding everything else fixed. See when the aggregate sign flips."""
    apply_style()
    rng = np.random.default_rng(0)
    n_total = 10000
    specs = [
        SegmentSpec("segment A", 0.20, 0.80, 0.05),
        SegmentSpec("segment B", 0.80, 0.20, 0.05),
    ]
    shares_a = np.linspace(0.05, 0.95, 31)
    aggregates = []
    for s_a in shares_a:
        # We hold per-segment effect at +0.05 in both; we vary treatment share imbalance.
        treatment_share = {"segment A": float(s_a), "segment B": 1.0 - float(s_a)}
        pop = imbalanced_assignment(n_total, specs, treatment_share, seed=int(rng.integers(0, 2**30)))
        c = np.concatenate([pop[s.name]["control"] for s in specs])
        t = np.concatenate([pop[s.name]["treatment"] for s in specs])
        aggregates.append(t.mean() - c.mean())

    save_samples(np.column_stack([shares_a, aggregates]), DATA_DIR / "paradox_sweep", seed=0, meta={"shares_a": shares_a.tolist()})

    fig, ax = plt.subplots()
    ax.plot(shares_a, aggregates, color=PALETTE["frequentist"])
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.axhline(0.05, color=PALETTE["highlight"], linestyle=":", linewidth=1, label="true within-segment effect = +0.05")
    ax.set_xlabel("treatment share in segment A (assignment imbalance)")
    ax.set_ylabel("aggregate treatment - control")
    ax.set_title("Loop B: when does the aggregate sign flip? (segments fixed at +0.05 each)")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "paradox_sweep.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_when_impossible():
    """Sketch: show the Simpson's-paradox condition can't trigger when assignment is balanced, even with skewed populations."""
    apply_style()
    rng = np.random.default_rng(0)
    n_total = 10000
    specs = [
        SegmentSpec("segment A", 0.20, 0.80, 0.05),
        SegmentSpec("segment B", 0.80, 0.20, 0.05),
    ]
    aggregates_balanced = []
    aggregates_imbalanced = []
    for trial in range(50):
        bal = imbalanced_assignment(n_total, specs, {"segment A": 0.5, "segment B": 0.5}, seed=int(rng.integers(0, 2**30)))
        imb = imbalanced_assignment(n_total, specs, {"segment A": 0.2, "segment B": 0.8}, seed=int(rng.integers(0, 2**30)))
        c = np.concatenate([bal[s.name]["control"] for s in specs])
        t = np.concatenate([bal[s.name]["treatment"] for s in specs])
        aggregates_balanced.append(t.mean() - c.mean())
        c2 = np.concatenate([imb[s.name]["control"] for s in specs])
        t2 = np.concatenate([imb[s.name]["treatment"] for s in specs])
        aggregates_imbalanced.append(t2.mean() - c2.mean())

    fig, ax = plt.subplots()
    ax.hist(aggregates_balanced, bins=20, alpha=0.6, color=PALETTE["frequentist"], label=f"balanced (50/50): mean = {np.mean(aggregates_balanced):+.3f}")
    ax.hist(aggregates_imbalanced, bins=20, alpha=0.6, color=PALETTE["bayesian"], label=f"imbalanced (20/80): mean = {np.mean(aggregates_imbalanced):+.3f}")
    ax.axvline(0.05, color=PALETTE["highlight"], linestyle=":", linewidth=1, label="true within-segment effect")
    ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_xlabel("aggregate treatment - control")
    ax.set_ylabel("count of simulated experiments")
    ax.set_title("Loop C: balanced assignment makes Simpson's paradox impossible")
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = IMG_DIR / "paradox_impossible.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_berkeley_style():
    """Classic Berkeley-style table where overall acceptance rate looks unfair, but department-level looks fair or reversed."""
    apply_style()
    # Two departments. Dept A is hard (low acceptance) and 80% of female applicants apply here.
    # Dept B is easy (high acceptance) and 80% of male applicants apply here.
    # Within each department, women have a SLIGHTLY higher acceptance rate.
    n_male, n_female = 1500, 1500
    rng = np.random.default_rng(0)
    male_dept = rng.choice(["A", "B"], size=n_male, p=[0.20, 0.80])
    female_dept = rng.choice(["A", "B"], size=n_female, p=[0.80, 0.20])
    dept_accept = {"A": {"male": 0.20, "female": 0.22}, "B": {"male": 0.65, "female": 0.67}}
    male_acc = np.array([rng.binomial(1, dept_accept[d]["male"]) for d in male_dept])
    female_acc = np.array([rng.binomial(1, dept_accept[d]["female"]) for d in female_dept])

    # Aggregate
    male_overall = male_acc.mean()
    female_overall = female_acc.mean()

    # Per-department
    a_male = male_acc[male_dept == "A"].mean()
    a_female = female_acc[female_dept == "A"].mean()
    b_male = male_acc[male_dept == "B"].mean()
    b_female = female_acc[female_dept == "B"].mean()

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6), sharey=True)
    axes[0].bar(["male", "female"], [male_overall, female_overall], color=[PALETTE["frequentist"], PALETTE["bayesian"]])
    axes[0].set_title(f"Aggregate: male {male_overall:.2f}, female {female_overall:.2f}")
    axes[1].bar(["male", "female"], [a_male, a_female], color=[PALETTE["frequentist"], PALETTE["bayesian"]])
    axes[1].set_title(f"Dept A: male {a_male:.2f}, female {a_female:.2f}")
    axes[2].bar(["male", "female"], [b_male, b_female], color=[PALETTE["frequentist"], PALETTE["bayesian"]])
    axes[2].set_title(f"Dept B: male {b_male:.2f}, female {b_female:.2f}")
    for ax in axes:
        ax.set_ylim(0, 1)
        ax.set_ylabel("acceptance rate")
    fig.suptitle("Loop E: Berkeley-style example -- aggregate looks unfair, per-department is fair")
    fig.tight_layout()
    out = IMG_DIR / "berkeley_style.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_paradox_construction(),
        render_when_does_it_flip(manifest),
        render_when_impossible(),
        render_berkeley_style(),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 12 figure: {p.name}")
    samples = DATA_DIR / "paradox_sweep.npy"
    if samples.exists():
        add_artifact(manifest, path=samples, kind="samples", seed=0, sha256=_sha256_file(samples), description="Loop B: paradox sweep over assignment imbalance")
    save_manifest(manifest)
    print(f"Chapter 12: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
