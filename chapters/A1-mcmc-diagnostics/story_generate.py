"""Regenerate Appendix A1 (MCMC diagnostics) story-track figures."""

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

CHAPTER = "A1-mcmc-diagnostics"
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


def render_good_vs_bad_trace():
    apply_story_style()
    rng = np.random.default_rng(606)
    n_draws = 1000
    # Good: well-mixing chain (random walk around truth)
    good_chain1 = 0.55 + rng.normal(0, 0.05, n_draws).cumsum() * 0.01
    good_chain1 = np.clip(good_chain1, 0.3, 0.8)
    good_chain2 = 0.55 + rng.normal(0, 0.05, n_draws).cumsum() * 0.01
    good_chain2 = np.clip(good_chain2, 0.3, 0.8)
    # Bad: stuck chain (slow mixing)
    bad_chain1 = np.concatenate([
        np.full(400, 0.45) + rng.normal(0, 0.01, 400),
        np.linspace(0.45, 0.62, 100),
        np.full(500, 0.62) + rng.normal(0, 0.01, 500)
    ])
    bad_chain2 = 0.62 + rng.normal(0, 0.005, n_draws)

    fig, axes = plt.subplots(1, 2, figsize=(13, 3.8))
    axes[0].plot(good_chain1, color=PALETTE["focus"], linewidth=0.8, alpha=0.8, label="chain 1")
    axes[0].plot(good_chain2, color=PALETTE["contrast"], linewidth=0.8, alpha=0.8, label="chain 2")
    axes[0].set_ylabel("parameter value")
    axes[0].set_xlabel("draw number")
    axes[0].set_title("healthy trace: chains mix, overlap, look like a fuzzy caterpillar\n(R-hat ≈ 1.00, no divergences)")
    axes[0].legend(fontsize=8)

    axes[1].plot(bad_chain1, color=PALETTE["focus"], linewidth=0.8, alpha=0.8, label="chain 1 (stuck early)")
    axes[1].plot(bad_chain2, color=PALETTE["contrast"], linewidth=0.8, alpha=0.8, label="chain 2")
    axes[1].set_ylabel("parameter value")
    axes[1].set_xlabel("draw number")
    axes[1].set_title("unhealthy trace: one chain stuck at 0.45 for 400 draws, then jumps\n(R-hat > 1.1 — inference not trustworthy)")
    axes[1].legend(fontsize=8)
    out = IMG_DIR / "good_vs_bad_trace.png"
    fig.savefig(out); plt.close(fig); return out


def main():
    ensure_dirs()
    paths = [(render_good_vs_bad_trace(), 606, "Story A1: healthy vs unhealthy MCMC trace")]
    print(f"Story A1: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
