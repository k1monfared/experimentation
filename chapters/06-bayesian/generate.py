"""Regenerate Chapter 6 (Bayesian formalized) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy.stats import beta as beta_dist

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.inference.bayes import (  # noqa: E402
    bayes_factor_point_vs_uniform,
    coin_posterior,
    conjugate_posterior_predictive,
)
from expkit.io.samples import _sha256_file, save_idata, save_samples  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.sim.coin import bernoulli_sequence  # noqa: E402

CHAPTER = "06-bayesian"
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


def render_priors_argue(manifest):
    """Same 6/10 data, four priors. Then same 600/1000 with the same priors."""
    apply_style()
    priors = [
        ("Beta(1, 1) flat", 1.0, 1.0),
        ("Beta(50, 50) skeptical", 50.0, 50.0),
        ("Beta(2, 8) expects-tails", 2.0, 8.0),
        ("Beta(8, 2) expects-heads", 8.0, 2.0),
    ]
    cases = [(6, 10), (600, 1000)]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.0), sharey=False)
    ps = np.linspace(0, 1, 1000)
    cmap = plt.get_cmap("viridis")
    for ax, (k, n) in zip(axes, cases):
        for j, (name, a0, b0) in enumerate(priors):
            post_a, post_b = a0 + k, b0 + (n - k)
            ax.plot(ps, beta_dist.pdf(ps, post_a, post_b), color=cmap(j / max(1, len(priors) - 1)), label=f"{name}")
        ax.axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.set_xlabel("p")
        ax.set_ylabel("posterior density")
        ax.set_title(f"{k}/{n}")
        ax.legend(fontsize=8)
    fig.suptitle("Loop B: priors argue. At small N they win. At large N the data wins.")
    fig.tight_layout()
    out = IMG_DIR / "priors_argue.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_pymc_diagnostic(manifest):
    """Run a PyMC fit and show its trace alongside the closed-form posterior."""
    apply_style()
    seq = bernoulli_sequence(200, p=0.55, seed=7)
    idata = coin_posterior(seq, seed=606, draws=2000, chains=2, tune=1000, progressbar=False)
    res = save_idata(idata, DATA_DIR / "posterior_chapter6", seed=606, meta={"n": 200, "p_true": 0.55, "prior": "Beta(1,1)"})
    add_artifact(manifest, path=res.path, kind="idata", seed=606, sha256=res.sha256, description="Chapter 6 PyMC posterior on p (200 tosses, p=0.55)")

    p_samples = idata.posterior["p"].values.ravel()
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
    # Trace plot (one chain at a time)
    for chain in range(idata.posterior.sizes["chain"]):
        axes[0].plot(idata.posterior["p"].values[chain], alpha=0.6, label=f"chain {chain}")
    axes[0].set_xlabel("draw")
    axes[0].set_ylabel("p")
    axes[0].set_title("PyMC trace (mixing)")
    axes[0].legend()
    # Histogram + closed-form Beta overlay
    a, b = 1 + int(seq.sum()), 1 + (seq.size - int(seq.sum()))
    ps = np.linspace(0, 1, 1000)
    axes[1].hist(p_samples, bins=60, density=True, color=PALETTE["bayesian"], alpha=0.55, label="PyMC posterior samples")
    axes[1].plot(ps, beta_dist.pdf(ps, a, b), color=PALETTE["frequentist"], linewidth=2, label=f"closed-form Beta({a}, {b})")
    axes[1].axvline(0.55, color=PALETTE["muted"], linestyle="--", linewidth=1, label="true p = 0.55")
    axes[1].set_xlabel("p")
    axes[1].set_ylabel("density")
    axes[1].set_title("PyMC matches the closed form")
    axes[1].legend()
    fig.tight_layout()
    out = IMG_DIR / "pymc_trace_vs_closed_form.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_bayes_factor(manifest=None):
    """Bayes factor curve as evidence accumulates.

    Saves the (N, BF_fair, BF_biased) curve to data/bayes_factor_curve.npy
    so the chapter prose can cite specific N->BF numbers from a sidecar.
    """
    apply_style()
    rng = np.random.default_rng(0)
    fair = rng.binomial(1, 0.5, size=2000)
    biased = rng.binomial(1, 0.55, size=2000)
    ns = np.unique(np.round(np.geomspace(5, 2000, 80)).astype(int))
    bfs_fair = []
    bfs_biased = []
    for n in ns:
        bfs_fair.append(bayes_factor_point_vs_uniform(fair[:n], point=0.5))
        bfs_biased.append(bayes_factor_point_vs_uniform(biased[:n], point=0.5))

    # Save the curve so chapter prose can quote specific (N, BF) values from a manifest entry.
    from expkit.io.samples import save_samples
    arr = np.column_stack([ns, np.array(bfs_fair), np.array(bfs_biased)])
    res = save_samples(
        arr,
        DATA_DIR / "bayes_factor_curve",
        seed=0,
        meta={"columns": ["N", "BF_fair", "BF_biased"], "p_alt_uniform": True, "true_p_biased": 0.55},
    )
    if manifest is not None:
        add_artifact(
            manifest, path=res.path, kind="samples", seed=0, sha256=res.sha256,
            description="Loop D: BF_10 vs N for a fair and a biased coin",
        )

    fig, ax = plt.subplots()
    ax.plot(ns, bfs_fair, color=PALETTE["frequentist"], label="data from fair coin")
    ax.plot(ns, bfs_biased, color=PALETTE["bayesian"], label="data from p = 0.55")
    ax.axhline(1, color=PALETTE["muted"], linestyle="--", linewidth=1, label="BF = 1 (no evidence)")
    ax.axhline(10, color=PALETTE["highlight"], linestyle=":", linewidth=1, label="BF = 10 (strong for H1)")
    ax.axhline(0.1, color=PALETTE["highlight"], linestyle=":", linewidth=1, label="BF = 0.1 (strong for H0)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("N (log scale)")
    ax.set_ylabel("BF_10 (large = data favours alternative)")
    ax.set_title("Loop D: Bayes factor accumulates evidence with N")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "bayes_factor.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_posterior_predictive():
    """Posterior predictive of how many heads we'd see in the NEXT 20 tosses."""
    apply_style()
    seq = bernoulli_sequence(50, p=0.6, seed=11)
    preds = conjugate_posterior_predictive(seq, new_n=20, n_samples=10000, seed=0)
    fig, ax = plt.subplots()
    bins = np.arange(-0.5, 21.5, 1.0)
    ax.hist(preds, bins=bins, density=True, color=PALETTE["bayesian"], alpha=0.7, label="posterior predictive")
    ax.axvline(0.5 * 20, color=PALETTE["muted"], linestyle="--", linewidth=1, label="if fair: expected 10")
    ax.axvline(0.6 * 20, color=PALETTE["highlight"], linestyle=":", linewidth=1, label="if true p=0.6: expected 12")
    ax.set_xlabel("heads in next 20 tosses")
    ax.set_ylabel("posterior predictive density")
    ax.set_title("Loop E: posterior predictive answers a different question -- what will I see next?")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "posterior_predictive.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_priors_argue(manifest),
        render_pymc_diagnostic(manifest),
        render_bayes_factor(manifest),
        render_posterior_predictive(),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 6 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 6: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
