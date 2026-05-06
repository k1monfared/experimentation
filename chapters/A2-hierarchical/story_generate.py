"""Regenerate Appendix A2 (Hierarchical Bayes) story-track figures."""

from __future__ import annotations
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.plot.story import PALETTE, apply_story_style  # noqa: E402

CHAPTER = "A2-hierarchical"
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


def render_shrinkage_illustration():
    apply_story_style()
    rng = np.random.default_rng(42)
    n_segments = 12
    true_effects = rng.normal(0.05, 0.04, size=n_segments)
    sample_sizes = np.array([30, 50, 80, 120, 150, 200, 250, 300, 400, 500, 800, 1000])
    noise = np.array([np.sqrt(0.25/n) for n in sample_sizes])
    observed = true_effects + rng.normal(0, noise)
    pop_mean = true_effects.mean()
    # Hierarchical estimate: shrink toward pop_mean
    # Simple approximation: weighted average of observed and pop_mean by precision
    sigma_pop = 0.04
    sigma_within = noise
    w_obs = 1 / sigma_within**2
    w_pop = 1 / sigma_pop**2
    hierarchical = (w_obs * observed + w_pop * pop_mean) / (w_obs + w_pop)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    xs = np.arange(n_segments)
    ax.scatter(xs - 0.15, observed * 100, s=sample_sizes/5, color=PALETTE["focus"], alpha=0.7, label="naive estimate (per-segment)")
    ax.scatter(xs + 0.15, hierarchical * 100, s=50, color=PALETTE["contrast"], alpha=0.9, label="hierarchical estimate (shrunk)")
    for i in range(n_segments):
        ax.plot([i - 0.15, i + 0.15], [observed[i]*100, hierarchical[i]*100],
                color=PALETTE["muted"], linewidth=0.8, alpha=0.6)
    ax.axhline(pop_mean * 100, color=PALETTE["ink"], linestyle="--", linewidth=1, label=f"population mean ({pop_mean*100:.1f}pp)")
    ax.set_xlabel(f"segment (left to right: smaller N to larger N, n={sample_sizes[0]} to {sample_sizes[-1]})")
    ax.set_ylabel("treatment effect estimate (pp)")
    ax.set_title("hierarchical shrinkage: small-N segments pulled toward population mean, large-N segments stay put")
    ax.legend(fontsize=8)
    out = IMG_DIR / "shrinkage_illustration.png"
    fig.savefig(out); plt.close(fig); return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [(render_shrinkage_illustration(), 42, "Story A2: hierarchical shrinkage by segment size")]
    for path, seed, desc in paths:
        add_artifact(manifest, path=path, kind="image", seed=seed, sha256=_sha256_file(path), description=desc)
    save_manifest(manifest)
    print(f"Story A2: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
