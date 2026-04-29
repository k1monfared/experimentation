"""Regenerate Chapter 15 (dilution) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.metrics.delta import delta_two_arm, ratio_mean_and_var  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.sim.dilution import settings_page_experiment  # noqa: E402

CHAPTER = "15-dilution"
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


def render_itt_vs_per_protocol():
    apply_style()
    df = settings_page_experiment(n_users=20000, visit_prob=0.12, base_rate=0.20, treatment_lift_among_visitors=0.10, seed=150)
    itt_t = df[df["arm"] == "treatment"]["outcome"].mean()
    itt_c = df[df["arm"] == "control"]["outcome"].mean()
    pp_t = df[(df["arm"] == "treatment") & (df["visited"])]["outcome"].mean()
    pp_c = df[(df["arm"] == "control") & (df["visited"])]["outcome"].mean()
    fig, ax = plt.subplots()
    ax.bar(["ITT (all users)", "per-protocol (visited only)"], [itt_t - itt_c, pp_t - pp_c], color=[PALETTE["frequentist"], PALETTE["bayesian"]])
    ax.axhline(0.10, color=PALETTE["highlight"], linestyle=":", linewidth=1, label="true effect among visitors = +0.10")
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_ylabel("treatment - control")
    ax.set_title("Loop A: ITT dilutes the among-visitors effect by the visit rate")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "itt_vs_per_protocol.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_dilution_sweep():
    """As visit rate goes up, ITT effect approaches the true among-visitors effect."""
    apply_style()
    rng = np.random.default_rng(0)
    visit_probs = np.linspace(0.02, 0.95, 30)
    itts = []
    pps = []
    true_pp = 0.10
    for v in visit_probs:
        df = settings_page_experiment(n_users=8000, visit_prob=float(v), base_rate=0.20, treatment_lift_among_visitors=true_pp, seed=int(rng.integers(0, 2**30)))
        itts.append(df[df["arm"] == "treatment"]["outcome"].mean() - df[df["arm"] == "control"]["outcome"].mean())
        sub = df[df["visited"]]
        pps.append(sub[sub["arm"] == "treatment"]["outcome"].mean() - sub[sub["arm"] == "control"]["outcome"].mean())
    fig, ax = plt.subplots()
    ax.plot(visit_probs, itts, color=PALETTE["frequentist"], label="ITT effect")
    ax.plot(visit_probs, pps, color=PALETTE["bayesian"], label="per-protocol effect")
    ax.axhline(true_pp, color=PALETTE["highlight"], linestyle=":", linewidth=1, label=f"true among-visitors effect = {true_pp}")
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_xlabel("visit probability")
    ax.set_ylabel("measured treatment - control")
    ax.set_title("Loop B: ITT scales with the visit rate; per-protocol does not")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "dilution_sweep.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_ratio_metric():
    """Two-arm experiment on revenue / sessions. Naive z vs delta-method."""
    apply_style()
    rng = np.random.default_rng(0)
    n = 3000
    # Control: sessions = Poisson(8), revenue = Normal(2 * sessions, 4)
    sess_c = rng.poisson(8, n)
    rev_c = rng.normal(2.0 * sess_c, 4)
    # Treatment: same sessions, revenue lifted by 0.05 per session
    sess_t = rng.poisson(8, n)
    rev_t = rng.normal(2.05 * sess_t, 4)
    diff, se, z = delta_two_arm(rev_t, sess_t, rev_c, sess_c)
    naive_diff = (rev_t.sum() / sess_t.sum()) - (rev_c.sum() / sess_c.sum())
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.axis("off")
    ax.text(0.0, 0.7, f"naive ratio diff: {naive_diff:.4f} (no SE estimate)", fontsize=11)
    ax.text(0.0, 0.45, f"delta method: diff = {diff:.4f}, se = {se:.4f}, z = {z:.2f}", fontsize=11)
    ax.text(0.0, 0.2, "True effect: revenue per session up 0.05.", fontsize=11, style="italic")
    ax.set_title("Loop C: ratio metric (revenue / sessions). Delta method gives an SE; naive doesn't.")
    fig.tight_layout()
    out = IMG_DIR / "ratio_metric.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_itt_vs_per_protocol(),
        render_dilution_sweep(),
        render_ratio_metric(),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 15 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 15: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
