"""Regenerate Chapter 15 (Dilution / ITT) story-track figures."""

from __future__ import annotations
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.plot.story import PALETTE, apply_story_style  # noqa: E402

CHAPTER = "15-dilution"
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


def render_itt_vs_per_protocol():
    apply_story_style()
    rng = np.random.default_rng(15)
    n = 500
    compliance = 0.70  # only 70% of treatment arm actually takes the drug
    p_control = 0.30
    underlying_effect = 0.10  # real per-treatment effect

    # Simulate ITT (everyone in their assigned arm)
    s_c = rng.binomial(n, p_control)
    # Treatment arm: 70% take drug (get the effect), 30% don't
    s_t_compliers = rng.binomial(int(n * compliance), p_control + underlying_effect)
    s_t_noncompliers = rng.binomial(n - int(n * compliance), p_control)
    s_t_itt = s_t_compliers + s_t_noncompliers
    n_t_compliers = int(n * compliance)
    s_c_compliers = rng.binomial(n_t_compliers, p_control)  # matched control compliers

    itt_diff = s_t_itt / n - s_c / n
    pp_diff = s_t_compliers / n_t_compliers - s_c_compliers / n_t_compliers
    true_diff = underlying_effect

    fig, ax = plt.subplots(figsize=(10, 4.5))
    analyses = ["intent-to-treat\n(everyone assigned)", "per-protocol\n(only those who took drug)", "truth\n(actual per-treatment effect)"]
    diffs = [itt_diff, pp_diff, true_diff]
    colors = [PALETTE["focus"], PALETTE["contrast"], PALETTE["muted"]]
    bars = ax.bar(analyses, [d * 100 for d in diffs], color=colors, width=0.6)
    for b, d in zip(bars, diffs):
        ax.text(b.get_x() + b.get_width() / 2, d * 100 + 0.3, f"{d * 100:+.1f}pp",
                ha="center", fontsize=11)
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_ylabel("measured effect (percentage points)")
    ax.set_title(f"70% compliance. ITT dilutes the real effect; per-protocol recovers it (but has selection bias risk).")
    out = IMG_DIR / "itt_vs_per_protocol.png"
    fig.savefig(out); plt.close(fig)
    return out, {"itt": round(itt_diff, 4), "pp": round(pp_diff, 4), "true": true_diff}


def render_compliance_sweep():
    apply_story_style()
    compliance_rates = np.linspace(0.2, 1.0, 50)
    rng = np.random.default_rng(15)
    p_c = 0.30; eff = 0.10; n = 2000
    s_c = rng.binomial(n, p_c)
    itts = []
    for cr in compliance_rates:
        s_compliers = rng.binomial(int(n * cr), p_c + eff)
        s_non = rng.binomial(n - int(n * cr), p_c)
        itts.append((s_compliers + s_non) / n - s_c / n)
    fig, ax = plt.subplots(figsize=(11, 4.0))
    ax.plot(compliance_rates * 100, np.array(itts) * 100, color=PALETTE["focus"], linewidth=2)
    ax.axhline(eff * 100, color=PALETTE["ink"], linestyle="--", linewidth=1, label=f"true effect (+{eff*100:.0f}pp)")
    ax.set_xlabel("fraction of treatment arm who actually took the drug (%)")
    ax.set_ylabel("intent-to-treat effect (pp)")
    ax.set_title("as compliance falls, the ITT estimate shrinks toward zero")
    ax.legend()
    out = IMG_DIR / "compliance_sweep.png"
    fig.savefig(out); plt.close(fig); return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    p1, nums = render_itt_vs_per_protocol()
    paths = [(p1, 15, f"Story Ch.15: ITT vs per-protocol, compliance 70%, values {nums}"),
             (render_compliance_sweep(), 15, "Story Ch.15: ITT effect vs compliance rate")]
    for path, seed, desc in paths:
        add_artifact(manifest, path=path, kind="image", seed=seed, sha256=_sha256_file(path), description=desc)
    save_manifest(manifest)
    print(f"Story Ch.15: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
