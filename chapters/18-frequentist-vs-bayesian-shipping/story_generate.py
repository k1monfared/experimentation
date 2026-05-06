"""Regenerate Chapter 18 (F vs B shipping) story-track figures."""

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
from expkit.plot.story import PALETTE, apply_story_style, reference_line  # noqa: E402

CHAPTER = "18-frequentist-vs-bayesian-shipping"
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


def render_framework_agreement():
    apply_story_style()
    rng = np.random.default_rng(18)
    n = 2000
    p_c = 0.05
    mmu = 0.005
    n_trials = 500
    effects = np.linspace(-0.02, 0.04, 15)
    freq_ship, bayes_ship, agree_rate = [], [], []
    for eff in effects:
        p_t = p_c + eff
        f = b = a = 0
        for _ in range(n_trials):
            s_c = rng.binomial(n, p_c)
            s_t = rng.binomial(n, max(0, min(1, p_t)))
            diff = s_t/n - s_c/n
            p_pool = (s_c + s_t) / (2*n)
            se = np.sqrt(p_pool*(1-p_pool)*2/n)
            pval = 2 * stats.norm.sf(abs(diff/se)) if se > 0 else 1.0
            freq_says = pval < 0.05 and diff > 0
            samples_c = rng.beta(1+s_c, 1+n-s_c, size=2000)
            samples_t = rng.beta(1+s_t, 1+n-s_t, size=2000)
            bayes_says = float((samples_t - samples_c > mmu).mean()) > 0.95
            f += freq_says; b += bayes_says
            if freq_says == bayes_says: a += 1
        freq_ship.append(f/n_trials); bayes_ship.append(b/n_trials); agree_rate.append(a/n_trials)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    axes[0].plot(effects*100, freq_ship, "o-", color=PALETTE["focus"], linewidth=1.8, label="frequentist (p<0.05 + positive)")
    axes[0].plot(effects*100, bayes_ship, "s-", color=PALETTE["contrast"], linewidth=1.8, label=f"Bayesian (P(lift>{mmu*100}pp)>0.95)")
    axes[0].axvline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[0].axvline(mmu*100, color=PALETTE["ink"], linestyle=":", linewidth=1)
    axes[0].set_xlabel("true effect (pp)"); axes[0].set_ylabel("ship rate")
    axes[0].set_title("shipping rate by true effect"); axes[0].legend(fontsize=8)
    axes[1].plot(effects*100, agree_rate, "o-", color=PALETTE["support"], linewidth=1.8)
    reference_line(axes[1], 0.9, label="90% agreement line")
    axes[1].set_xlabel("true effect (pp)"); axes[1].set_ylabel("fraction of experiments both agree")
    axes[1].set_title("agreement rate: two rules, same decision most of the time")
    axes[1].legend(fontsize=8)
    out = IMG_DIR / "framework_agreement.png"
    fig.savefig(out); plt.close(fig); return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [(render_framework_agreement(), 18, "Story Ch.18: freq vs Bayes shipping rates and agreement")]
    for path, seed, desc in paths:
        add_artifact(manifest, path=path, kind="image", seed=seed, sha256=_sha256_file(path), description=desc)
    save_manifest(manifest)
    print(f"Story Ch.18: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
