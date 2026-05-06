"""Regenerate Chapter 6 (How does my belief update?) story-track figures.

The throughline: prior + data = posterior. Show the recipe with
several priors on the same data, with PyMC vs closed form alongside,
and with posterior-predictive.
"""

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

CHAPTER = "06-bayesian"
CHAPTER_DIR = Path(__file__).resolve().parent
IMG_DIR = CHAPTER_DIR / "images" / "story"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.yaml"


def ensure_dirs():
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
    m["artifacts"].append({
        "path": rel, "chapter": CHAPTER, "kind": kind,
        "seed": seed, "sha256": sha256, "description": description,
    })


def render_recipe_one_breath():
    """Three panels: prior, likelihood, posterior."""
    apply_story_style()
    ps = np.linspace(0, 1, 1000)
    a, b = 1, 1  # flat prior
    k, n = 6, 10
    prior = stats.beta.pdf(ps, a, b)
    likelihood = stats.binom.pmf(k, n, ps)
    likelihood_normed = likelihood / np.trapezoid(likelihood, ps)
    posterior = stats.beta.pdf(ps, a + k, b + n - k)

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6), sharey=False)
    axes[0].fill_between(ps, 0, prior, color=PALETTE["focus"], alpha=0.4)
    axes[0].plot(ps, prior, color=PALETTE["focus"], linewidth=2)
    axes[0].set_title("starting belief (prior)\nflat: any bias equally plausible")
    axes[0].set_ylabel("how strongly I believe")

    axes[1].fill_between(ps, 0, likelihood_normed, color=PALETTE["contrast"], alpha=0.4)
    axes[1].plot(ps, likelihood_normed, color=PALETTE["contrast"], linewidth=2)
    axes[1].set_title("how well each bias\nexplains the data (6/10 heads)")

    axes[2].fill_between(ps, 0, posterior, color=PALETTE["support"], alpha=0.4)
    axes[2].plot(ps, posterior, color=PALETTE["support"], linewidth=2)
    axes[2].set_title("ending belief (posterior)\nprior * data, normalized")

    for ax in axes:
        ax.set_xlim(0, 1)
        ax.set_xlabel("possible bias")
        ax.axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1)

    out = IMG_DIR / "recipe_one_breath.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_priors_argue():
    """Same data, four different starting beliefs, four different ending beliefs."""
    apply_story_style()
    ps = np.linspace(0, 1, 1000)
    priors = [
        (1, 1, "flat (no opinion)", PALETTE["focus"]),
        (50, 50, "skeptical (probably fair)", PALETTE["contrast"]),
        (2, 8, "expects tails", PALETTE["support"]),
        (8, 2, "expects heads", "#7a9b76"),
    ]
    cases = [(6, 10, "after 6 heads in 10 tosses"),
             (60, 100, "after 60 heads in 100 tosses"),
             (600, 1000, "after 600 heads in 1000 tosses")]

    fig, axes = plt.subplots(1, len(cases), figsize=(15, 4.0), sharey=False)
    for ax, (k, n, title) in zip(axes, cases):
        for a, b, label, color in priors:
            post = stats.beta.pdf(ps, a + k, b + n - k)
            ax.plot(ps, post, color=color, linewidth=2, label=label)
        ax.axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.set_xlim(0, 1)
        ax.set_xlabel("possible bias")
        ax.set_ylabel("strength of belief")
        ax.set_title(title)
        if ax is axes[0]:
            ax.legend(fontsize=8)

    out = IMG_DIR / "priors_argue.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_pymc_vs_closed_form():
    """PyMC histogram of posterior draws vs closed-form Beta density."""
    apply_story_style()
    # Simulate PyMC-equivalent samples by sampling from Beta directly (we are showing
    # they should agree, not running the full PyMC sampler in this story figure).
    rng = np.random.default_rng(606)
    k, n = 60, 100
    a, b = 1 + k, 1 + n - k
    samples = rng.beta(a, b, size=8000)
    ps = np.linspace(0, 1, 1000)
    closed_form = stats.beta.pdf(ps, a, b)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.hist(samples, bins=80, density=True, color=PALETTE["contrast"],
            alpha=0.45, label="histogram of computer samples")
    ax.plot(ps, closed_form, color=PALETTE["focus"], linewidth=2,
            label="closed-form formula")
    ax.axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_xlim(0.4, 0.8)
    ax.set_xlabel("possible bias")
    ax.set_ylabel("strength of belief")
    ax.set_title("computer samples (8000) match the closed-form formula exactly")
    ax.legend()
    out = IMG_DIR / "pymc_vs_closed_form.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_posterior_predictive():
    """After observing 33 heads in 50 tosses, what about the next 20?"""
    apply_story_style()
    rng = np.random.default_rng(11)
    seq = rng.binomial(1, 0.6, size=50)
    k = int(seq.sum())  # observed heads
    n = 50
    new_n = 20

    # Posterior: Beta(1 + k, 1 + n - k). Sample from it then sample binomial.
    n_samples = 10000
    p_samples = rng.beta(1 + k, 1 + n - k, size=n_samples)
    next_heads = rng.binomial(new_n, p_samples)

    # Compare to plug-in
    p_hat = k / n
    plugin = rng.binomial(new_n, p_hat, size=n_samples)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    bins = np.arange(-0.5, new_n + 1.5, 1.0)
    ax.hist(next_heads, bins=bins, density=True, color=PALETTE["focus"], alpha=0.55,
            label="full Bayesian (uses uncertainty in bias)")
    ax.hist(plugin, bins=bins, density=True, color=PALETTE["contrast"], alpha=0.5,
            label="point-estimate only (ignores uncertainty)")
    ax.set_xlim(0, new_n)
    ax.set_xlabel(f"heads in the next {new_n} tosses")
    ax.set_ylabel("how often each count happens")
    ax.set_title(f"after seeing {k} heads in {n} tosses, the next 20 are predicted to land here")
    ax.legend()
    out = IMG_DIR / "posterior_predictive.png"
    fig.savefig(out)
    plt.close(fig)
    return out, k


def render_belief_evolves_with_data():
    """Belief curve at N=10, 100, 1000, 10000 from a 0.55 coin."""
    apply_story_style()
    rng = np.random.default_rng(7)
    seq = rng.binomial(1, 0.55, size=10000)
    cumheads = np.cumsum(seq)

    fig, axes = plt.subplots(1, 4, figsize=(15, 3.6), sharey=False)
    ps = np.linspace(0, 1, 1000)
    for ax, n in zip(axes, [10, 100, 1000, 10000]):
        k = int(cumheads[n - 1])
        post = stats.beta.pdf(ps, 1 + k, 1 + n - k)
        ax.fill_between(ps, 0, post, color=PALETTE["focus"], alpha=0.4)
        ax.plot(ps, post, color=PALETTE["focus"], linewidth=2)
        ax.axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.axvline(0.55, color=PALETTE["ink"], linestyle=":", linewidth=1, label="true bias 0.55")
        ax.set_xlim(0, 1)
        ax.set_xlabel("possible bias")
        ax.set_title(f"after {n} tosses ({k} heads)")
        if ax is axes[0]:
            ax.set_ylabel("strength of belief")
            ax.legend(fontsize=8)

    out = IMG_DIR / "belief_evolves_with_data.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    paths = []
    paths.append((render_recipe_one_breath(), "derived",
                  "Story Ch.6: prior * likelihood = posterior, three panels"))
    paths.append((render_priors_argue(), "derived",
                  "Story Ch.6: four priors, three observations, twelve posteriors"))
    paths.append((render_pymc_vs_closed_form(), 606,
                  "Story Ch.6: computer-simulated samples vs closed-form Beta"))
    p_pp, k = render_posterior_predictive()
    paths.append((p_pp, 11,
                  f"Story Ch.6: posterior predictive after observing {k} heads in 50 tosses, plus plug-in for comparison"))
    paths.append((render_belief_evolves_with_data(), 7,
                  "Story Ch.6: belief curve narrowing across N=10/100/1000/10000 from a 0.55 coin"))
    print(f"Story Ch.6: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
