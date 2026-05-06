"""Regenerate Chapter 16 (Metric quality / CUPED) story-track figures."""

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

CHAPTER = "16-metric-quality"
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


def render_cuped_variance_reduction():
    apply_story_style()
    rng = np.random.default_rng(16)
    n = 1000
    true_effect = 0.5
    pre = rng.normal(10.0, 4.0, size=n)  # pre-experiment revenue
    # Treatment arms
    control_raw = pre[:n//2] + rng.normal(0, 4.0, size=n//2)
    treat_raw = pre[n//2:] + true_effect + rng.normal(0, 4.0, size=n//2)
    # CUPED adjustment: subtract pre-experiment mean * theta
    theta = np.cov(control_raw, pre[:n//2])[0, 1] / np.var(pre[:n//2])
    control_cuped = control_raw - theta * (pre[:n//2] - pre[:n//2].mean())
    treat_cuped = treat_raw - theta * (pre[n//2:] - pre[n//2:].mean())
    diff_raw = treat_raw.mean() - control_raw.mean()
    diff_cuped = treat_cuped.mean() - control_cuped.mean()
    se_raw = np.sqrt(control_raw.var(ddof=1) / (n//2) + treat_raw.var(ddof=1) / (n//2))
    se_cuped = np.sqrt(control_cuped.var(ddof=1) / (n//2) + treat_cuped.var(ddof=1) / (n//2))

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    axes[0].scatter(pre[:n//2], control_raw, alpha=0.3, s=8, color=PALETTE["contrast"], label="control")
    axes[0].scatter(pre[n//2:], treat_raw, alpha=0.3, s=8, color=PALETTE["focus"], label="treatment")
    axes[0].set_xlabel("pre-experiment revenue per user")
    axes[0].set_ylabel("during-experiment revenue per user")
    axes[0].set_title(f"raw: diff={diff_raw:.3f} ± {se_raw:.3f}")
    axes[0].legend(fontsize=8)

    axes[1].scatter(pre[:n//2], control_cuped, alpha=0.3, s=8, color=PALETTE["contrast"])
    axes[1].scatter(pre[n//2:], treat_cuped, alpha=0.3, s=8, color=PALETTE["focus"])
    axes[1].set_xlabel("pre-experiment revenue per user")
    axes[1].set_ylabel("CUPED-adjusted residual")
    axes[1].set_title(f"after CUPED: diff={diff_cuped:.3f} ± {se_cuped:.3f} ({(1 - se_cuped/se_raw)*100:.0f}% variance reduction)")
    out = IMG_DIR / "cuped_variance_reduction.png"
    fig.savefig(out); plt.close(fig)
    return out, {"se_raw": round(se_raw, 4), "se_cuped": round(se_cuped, 4), "theta": round(theta, 4)}


def render_aa_test_distribution():
    apply_story_style()
    rng = np.random.default_rng(16)
    n_aa = 2000
    n_per_arm = 500
    diffs = []
    for _ in range(n_aa):
        a = rng.normal(10.0, 4.0, size=n_per_arm)
        b = rng.normal(10.0, 4.0, size=n_per_arm)
        diffs.append(b.mean() - a.mean())
    fig, ax = plt.subplots(figsize=(10, 4.0))
    ax.hist(diffs, bins=60, density=True, color=PALETTE["focus"], alpha=0.65, label=f"A/A differences ({n_aa} runs)")
    ax.axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    pct5 = np.percentile(diffs, 5)
    pct95 = np.percentile(diffs, 95)
    ax.axvline(pct5, color=PALETTE["ink"], linestyle=":", linewidth=1, label=f"5th/95th pct: [{pct5:.2f}, {pct95:.2f}]")
    ax.axvline(pct95, color=PALETTE["ink"], linestyle=":", linewidth=1)
    ax.set_xlabel("measured difference between identical arms")
    ax.set_ylabel("density")
    ax.set_title(f"A/A test: expected effect is zero, but noise gives apparent differences of ±{pct95:.2f}")
    ax.legend(fontsize=8)
    out = IMG_DIR / "aa_test_distribution.png"
    fig.savefig(out); plt.close(fig); return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    p1, nums = render_cuped_variance_reduction()
    paths = [(p1, 16, f"Story Ch.16: CUPED variance reduction, theta={nums['theta']}, se_raw={nums['se_raw']}, se_cuped={nums['se_cuped']}"),
             (render_aa_test_distribution(), 16, "Story Ch.16: A/A test null distribution")]
    for path, seed, desc in paths:
        add_artifact(manifest, path=path, kind="image", seed=seed, sha256=_sha256_file(path), description=desc)
    save_manifest(manifest)
    print(f"Story Ch.16: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
