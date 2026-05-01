"""Regenerate Appendix A2 (Hierarchical Bayesian deeper look) figures.

Three figures:
1. three_pooling_modes.png: per-segment estimates under no/complete/partial pooling.
2. tau_learned.png: posterior on tau across three true-tau scenarios + shrinkage.
3. prior_on_tau.png: same data, two priors on tau, watch posteriors split.

Bayesian fits use a logistic hierarchical model on segmented A/B success counts.
"""

from __future__ import annotations

import sys
from pathlib import Path

import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pymc as pm
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file, save_idata  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402

CHAPTER = "A2-hierarchical"
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


def simulate_segments(true_effects, sizes, base_p, seed):
    """Return per-segment success counts and totals for control and treatment."""
    rng = np.random.default_rng(seed)
    out = []
    for eff, n in zip(true_effects, sizes):
        n_c = n
        n_t = n
        s_c = rng.binomial(n_c, base_p)
        s_t = rng.binomial(n_t, np.clip(base_p + eff, 1e-4, 1 - 1e-4))
        out.append({"n_c": n_c, "s_c": int(s_c), "n_t": n_t, "s_t": int(s_t)})
    return out


def fit_hierarchical(data, prior_tau_sigma=0.1, seed=0, draws=1500, tune=1500):
    """Fit logit-link hierarchical model on per-segment success counts.

    Returns InferenceData. The model:
      baseline_s ~ Normal(0, 2)
      mu ~ Normal(0, 1)
      tau ~ HalfNormal(prior_tau_sigma)
      effect_s = mu + tau * z_s, z_s ~ Normal(0, 1)
      p_c[s] = sigmoid(baseline_s)
      p_t[s] = sigmoid(baseline_s + effect_s)
    """
    K = len(data)
    s_c = np.array([d["s_c"] for d in data])
    n_c = np.array([d["n_c"] for d in data])
    s_t = np.array([d["s_t"] for d in data])
    n_t = np.array([d["n_t"] for d in data])
    with pm.Model() as model:
        baseline = pm.Normal("baseline", mu=0, sigma=2, shape=K)
        mu = pm.Normal("mu", mu=0, sigma=1)
        tau = pm.HalfNormal("tau", sigma=prior_tau_sigma)
        z = pm.Normal("z", mu=0, sigma=1, shape=K)
        effect = pm.Deterministic("effect", mu + tau * z)
        p_c = pm.Deterministic("p_c", pm.math.sigmoid(baseline))
        p_t = pm.Deterministic("p_t", pm.math.sigmoid(baseline + effect))
        pm.Binomial("obs_c", n=n_c, p=p_c, observed=s_c)
        pm.Binomial("obs_t", n=n_t, p=p_t, observed=s_t)
        idata = pm.sample(draws, tune=tune, chains=2, random_seed=seed, progressbar=False, target_accept=0.95)
    return idata


def render_three_pooling_modes(manifest):
    apply_style()
    rng = np.random.default_rng(101)
    K = 8
    base_p = 0.30
    true_effects = rng.normal(0.05, 0.04, size=K)
    sizes = [800, 800, 800, 800, 80, 80, 80, 80]
    data = simulate_segments(true_effects, sizes, base_p, seed=101)

    # No pooling: independent per-segment z-test point estimate.
    indep = np.array([d["s_t"] / d["n_t"] - d["s_c"] / d["n_c"] for d in data])
    # Complete pooling: pooled rate diff across all segments.
    total_s_c = sum(d["s_c"] for d in data)
    total_n_c = sum(d["n_c"] for d in data)
    total_s_t = sum(d["s_t"] for d in data)
    total_n_t = sum(d["n_t"] for d in data)
    pooled = total_s_t / total_n_t - total_s_c / total_n_c

    idata = fit_hierarchical(data, prior_tau_sigma=0.5, seed=2002)
    res = save_idata(idata, DATA_DIR / "three_pooling_modes", seed=2002, meta={
        "true_effects": list(map(float, true_effects)),
        "sizes": sizes,
        "base_p": base_p,
    })
    add_artifact(manifest, path=res.path, kind="idata", seed=2002, sha256=res.sha256, description="A2 three-pooling-modes hierarchical posterior")

    p_t = idata.posterior["p_t"].values
    p_c = idata.posterior["p_c"].values
    diffs = (p_t - p_c).reshape(-1, K)
    partial_mean = diffs.mean(axis=0)
    partial_lo = np.quantile(diffs, 0.025, axis=0)
    partial_hi = np.quantile(diffs, 0.975, axis=0)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    xs = np.arange(K)
    ax.scatter(xs - 0.2, indep, s=70, color=PALETTE["frequentist"], label="no pooling", marker="s")
    ax.axhline(pooled, color=PALETTE["highlight"], linestyle=":", linewidth=1, label=f"complete pooling = {pooled:+.3f}")
    ax.errorbar(xs + 0.2, partial_mean, yerr=[partial_mean - partial_lo, partial_hi - partial_mean], fmt="o", color=PALETTE["bayesian"], capsize=4, label="partial pooling (95% CI)")
    for i, eff in enumerate(true_effects):
        ax.scatter(i, eff, s=100, marker="x", color=PALETTE["muted"], label="true effect" if i == 0 else None, zorder=3)
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"seg{i} (n={sizes[i]})" for i in range(K)], rotation=20, fontsize=8)
    ax.set_ylabel("treatment - control rate")
    ax.set_title("Loop A: same data, three estimators. Small segments shrink the most.")
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    out = IMG_DIR / "three_pooling_modes.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_tau_learned(manifest):
    apply_style()
    K = 8
    base_p = 0.30
    sizes = [400] * K
    scenarios = [(0.005, 1010), (0.04, 2020), (0.15, 3030)]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.0), sharey=False)
    for ax, (tau_true, seed) in zip(axes, scenarios):
        rng = np.random.default_rng(seed)
        true_effects = rng.normal(0.05, tau_true, size=K)
        data = simulate_segments(true_effects, sizes, base_p, seed=seed)
        idata = fit_hierarchical(data, prior_tau_sigma=0.1, seed=seed + 1)
        tau = idata.posterior["tau"].values.ravel()
        ax.hist(tau, bins=60, density=True, color=PALETTE["bayesian"], alpha=0.65)
        ax.axvline(tau_true, color=PALETTE["highlight"], linestyle=":", linewidth=2, label=f"true tau = {tau_true:.3f}")
        ax.set_xlabel("tau (population scale of segment effects, prob scale)")
        ax.set_ylabel("posterior density")
        ax.set_title(f"true tau = {tau_true:.3f}\nposterior mean = {tau.mean():.3f}")
        ax.legend(fontsize=8)

        tag = f"{tau_true:.3f}".replace(".", "p")
        res = save_idata(idata, DATA_DIR / f"tau_scenario_{tag}", seed=seed + 1, meta={"tau_true": tau_true})
        add_artifact(manifest, path=res.path, kind="idata", seed=seed + 1, sha256=res.sha256, description=f"A2 tau scenario tau_true={tau_true}")
    fig.suptitle("Loop B: tau is learned. The posterior on tau tells the story of how different the segments are.")
    fig.tight_layout()
    out = IMG_DIR / "tau_learned.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_prior_on_tau(manifest):
    apply_style()
    K = 8
    base_p = 0.30
    sizes = [400, 400, 400, 400, 40, 40, 40, 40]
    rng = np.random.default_rng(404)
    true_effects = rng.normal(0.05, 0.04, size=K)
    data = simulate_segments(true_effects, sizes, base_p, seed=404)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=False)
    for ax, (sigma, label) in zip(axes, [(0.05, "HalfNormal(0.05)"), (0.5, "HalfNormal(0.5)")]):
        idata = fit_hierarchical(data, prior_tau_sigma=sigma, seed=44 + int(sigma * 100))
        tau = idata.posterior["tau"].values.ravel()
        effect = idata.posterior["effect"].values.reshape(-1, K)
        ax.hist(tau, bins=60, density=True, color=PALETTE["bayesian"], alpha=0.55, label=f"posterior tau, prior {label}")
        ax.axvline(0.04, color=PALETTE["highlight"], linestyle=":", linewidth=2, label="true tau = 0.04")
        ax.axvline(tau.mean(), color="black", linestyle="-", linewidth=1, alpha=0.6, label=f"post mean = {tau.mean():.3f}")
        ax.set_xlabel("tau (logit-scale population spread)")
        ax.set_ylabel("posterior density")
        ax.set_title(f"prior tau ~ {label}\npost mean tau = {tau.mean():.3f}")
        ax.legend(fontsize=8)

        tag = f"{sigma:.2f}".replace(".", "p")
        res = save_idata(idata, DATA_DIR / f"prior_on_tau_{tag}", seed=44 + int(sigma * 100), meta={"prior_tau_sigma": sigma})
        add_artifact(manifest, path=res.path, kind="idata", seed=44 + int(sigma * 100), sha256=res.sha256, description=f"A2 prior-on-tau sigma={sigma}")
    fig.suptitle("Loop C: same data, two priors on tau. With weak data, the prior leads.")
    fig.tight_layout()
    out = IMG_DIR / "prior_on_tau.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_three_pooling_modes(manifest),
        render_tau_learned(manifest),
        render_prior_on_tau(manifest),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Appendix A2 figure: {p.name}")
    save_manifest(manifest)
    print(f"Appendix A2: wrote {len(paths)} figures + multiple PyMC traces")


if __name__ == "__main__":
    main()
