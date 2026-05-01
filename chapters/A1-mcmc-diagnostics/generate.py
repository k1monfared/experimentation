"""Regenerate Appendix A1 (MCMC diagnostics) figures.

Three figures:
1. healthy_chains.png: Ch.6-style coin model, 4 chains, perfect diagnostics.
2. funnel_centered_vs_noncentered.png: Neal's funnel fit with both
   parameterizations side by side; show divergence counts.
3. rhat_ess_curves.png: R-hat and ESS as a function of post-tuning draws,
   for both the healthy model and the centered funnel.

We deliberately keep the Neal funnel small (groups = 8 latent z, weak data)
so the centered run divergences are visible without burning minutes.
"""

from __future__ import annotations

import sys
import warnings
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

CHAPTER = "A1-mcmc-diagnostics"
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


def render_healthy_chains(manifest):
    apply_style()
    rng = np.random.default_rng(7)
    seq = rng.binomial(1, 0.55, size=200)
    with pm.Model():
        p = pm.Beta("p", alpha=1, beta=1)
        pm.Binomial("obs", n=len(seq), p=p, observed=int(seq.sum()))
        idata = pm.sample(2000, tune=1000, chains=4, random_seed=606, progressbar=False)
    rhat = float(az.rhat(idata).p.values)
    ess = float(az.ess(idata).p.values)
    div = int(idata.sample_stats["diverging"].sum().item())

    res = save_idata(idata, DATA_DIR / "healthy_chains", seed=606, meta={"n": 200, "p_true": 0.55, "model": "Beta(1,1) + Binomial"})
    add_artifact(manifest, path=res.path, kind="idata", seed=606, sha256=res.sha256, description="Appendix A1 healthy-chain coin posterior")

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))
    p_samples = idata.posterior["p"].values
    for c in range(p_samples.shape[0]):
        axes[0].plot(p_samples[c], alpha=0.65, label=f"chain {c}")
    axes[0].set_xlabel("draw")
    axes[0].set_ylabel("p")
    axes[0].set_title(f"trace (R-hat={rhat:.3f}, ESS={ess:.0f}, div={div})")
    axes[0].legend(fontsize=7, ncol=2)

    az.plot_autocorr(idata, var_names=["p"], ax=axes[1], combined=True)
    axes[1].set_title("autocorrelation by lag")

    flat = p_samples.ravel()
    axes[2].hist(flat, bins=60, density=True, color=PALETTE["bayesian"], alpha=0.6)
    axes[2].axvline(0.55, color=PALETTE["muted"], linestyle="--", linewidth=1, label="true p = 0.55")
    axes[2].set_xlabel("p")
    axes[2].set_ylabel("posterior density")
    axes[2].set_title("posterior on p")
    axes[2].legend()

    fig.suptitle("Loop A: a healthy sampler")
    fig.tight_layout()
    out = IMG_DIR / "healthy_chains.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_funnel(manifest):
    """Neal's funnel, centered vs non-centered parameterization."""
    apply_style()
    n_groups = 8
    rng = np.random.default_rng(42)
    # No "data" -- just the prior funnel. Fit both forms.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        # Centered form: theta_i ~ Normal(mu, tau), tau ~ HalfNormal.
        with pm.Model() as centered:
            mu = pm.Normal("mu", mu=0, sigma=1)
            tau = pm.HalfNormal("tau", sigma=1)
            pm.Normal("theta", mu=mu, sigma=tau, shape=n_groups)
            idata_c = pm.sample(
                2000, tune=1500, chains=4, random_seed=11, progressbar=False, target_accept=0.9
            )
        # Non-centered form: theta_i = mu + tau * z_i, z_i ~ Normal(0, 1).
        with pm.Model() as noncentered:
            mu = pm.Normal("mu", mu=0, sigma=1)
            tau = pm.HalfNormal("tau", sigma=1)
            z = pm.Normal("z", mu=0, sigma=1, shape=n_groups)
            pm.Deterministic("theta", mu + tau * z)
            idata_nc = pm.sample(
                2000, tune=1500, chains=4, random_seed=11, progressbar=False, target_accept=0.9
            )

    div_c = int(idata_c.sample_stats["diverging"].sum().item())
    div_nc = int(idata_nc.sample_stats["diverging"].sum().item())
    rhat_c = float(az.rhat(idata_c, var_names=["tau"]).tau.values)
    rhat_nc = float(az.rhat(idata_nc, var_names=["tau"]).tau.values)
    ess_c = float(az.ess(idata_c, var_names=["tau"]).tau.values)
    ess_nc = float(az.ess(idata_nc, var_names=["tau"]).tau.values)

    res_c = save_idata(idata_c, DATA_DIR / "funnel_centered", seed=11, meta={"parameterization": "centered", "n_groups": n_groups})
    res_nc = save_idata(idata_nc, DATA_DIR / "funnel_noncentered", seed=11, meta={"parameterization": "non-centered", "n_groups": n_groups})
    add_artifact(manifest, path=res_c.path, kind="idata", seed=11, sha256=res_c.sha256, description="Appendix A1 funnel fit, centered form")
    add_artifact(manifest, path=res_nc.path, kind="idata", seed=11, sha256=res_nc.sha256, description="Appendix A1 funnel fit, non-centered form")

    # Joint scatter of (theta_0, log tau) in each form to make the funnel visible.
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharex=True, sharey=True)
    log_tau_c = np.log(idata_c.posterior["tau"].values).ravel()
    theta0_c = idata_c.posterior["theta"].values[..., 0].ravel()
    log_tau_nc = np.log(idata_nc.posterior["tau"].values).ravel()
    theta0_nc = idata_nc.posterior["theta"].values[..., 0].ravel()

    axes[0].scatter(theta0_c, log_tau_c, s=4, alpha=0.35, color=PALETTE["frequentist"])
    axes[0].set_title(f"centered: div={div_c}, R-hat(tau)={rhat_c:.3f}, ESS(tau)={ess_c:.0f}")
    axes[0].set_xlabel("theta[0]")
    axes[0].set_ylabel("log(tau)")
    axes[1].scatter(theta0_nc, log_tau_nc, s=4, alpha=0.35, color=PALETTE["bayesian"])
    axes[1].set_title(f"non-centered: div={div_nc}, R-hat(tau)={rhat_nc:.3f}, ESS(tau)={ess_nc:.0f}")
    axes[1].set_xlabel("theta[0]")

    fig.suptitle("Loop B: same model, two parameterizations. The non-centered form fixes the geometry.")
    fig.tight_layout()
    out = IMG_DIR / "funnel_centered_vs_noncentered.png"
    fig.savefig(out)
    plt.close(fig)
    return out, {"centered": {"div": div_c, "rhat_tau": rhat_c, "ess_tau": ess_c}, "noncentered": {"div": div_nc, "rhat_tau": rhat_nc, "ess_tau": ess_nc}}


def render_rhat_ess_curves(manifest):
    """Show R-hat and ESS for the easy coin model as draws grow."""
    apply_style()
    rng = np.random.default_rng(303)
    seq = rng.binomial(1, 0.55, size=200)
    draws_grid = [200, 400, 800, 1500, 3000]
    rhats, esss = [], []
    for d in draws_grid:
        with pm.Model():
            p = pm.Beta("p", alpha=1, beta=1)
            pm.Binomial("obs", n=len(seq), p=p, observed=int(seq.sum()))
            idata = pm.sample(d, tune=500, chains=4, random_seed=606 + d, progressbar=False)
        rhats.append(float(az.rhat(idata).p.values))
        esss.append(float(az.ess(idata).p.values))

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    axes[0].plot(draws_grid, rhats, "o-", color=PALETTE["frequentist"])
    axes[0].axhline(1.01, color=PALETTE["highlight"], linestyle="--", linewidth=1, label="R-hat = 1.01 threshold")
    axes[0].set_xlabel("post-tuning draws per chain")
    axes[0].set_ylabel("R-hat on p")
    axes[0].set_title("R-hat shrinks toward 1 with more draws")
    axes[0].legend()
    axes[0].set_ylim(0.99, 1.05)

    axes[1].plot(draws_grid, esss, "o-", color=PALETTE["bayesian"])
    axes[1].set_xlabel("post-tuning draws per chain")
    axes[1].set_ylabel("ESS on p")
    axes[1].set_title("ESS grows roughly linearly with draws")

    fig.suptitle("Loop C: R-hat and ESS vs post-tuning draws (4 chains, healthy model)")
    fig.tight_layout()
    out = IMG_DIR / "rhat_ess_curves.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = []
    paths.append(render_healthy_chains(manifest))
    p, _ = render_funnel(manifest)
    paths.append(p)
    paths.append(render_rhat_ess_curves(manifest))
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Appendix A1 figure: {p.name}")
    save_manifest(manifest)
    print(f"Appendix A1: wrote {len(paths)} figures + 3 PyMC traces")


if __name__ == "__main__":
    main()
