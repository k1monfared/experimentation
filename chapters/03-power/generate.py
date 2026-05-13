"""Regenerate Chapter 3 (power) datasets and figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file, save_samples  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.power.binomial import (  # noqa: E402
    mde,
    normal_approx_power,
    required_n,
    simulate_rejection_rate,
)

CHAPTER = "03-power"
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


def render_power_curves():
    apply_style()
    ns = np.unique(np.round(np.geomspace(10, 10_000, 60)).astype(int))
    fig, ax = plt.subplots()
    cmap = plt.get_cmap("viridis")
    effects = [0.51, 0.52, 0.55, 0.60, 0.70]
    for i, p in enumerate(effects):
        powers = np.array([normal_approx_power(0.5, p, n=int(n)) for n in ns])
        ax.plot(ns, powers, color=cmap(i / max(1, len(effects) - 1)), label=f"p = {p}")
    ax.axhline(0.8, color=PALETTE["muted"], linestyle="--", linewidth=1, label="80% power")
    ax.set_xscale("log")
    ax.set_xlabel("sample size N (log scale)")
    ax.set_ylabel("power")
    ax.set_ylim(0, 1.05)
    ax.set_title("Loop A and B: power vs sample size for several effect sizes")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "power_curves.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_required_n_table():
    apply_style()
    effects = np.array([0.51, 0.52, 0.55, 0.60, 0.70])
    ns_at_80 = np.array([required_n(0.5, p, power=0.8, n_max=200_000) for p in effects])
    ns_at_95 = np.array([required_n(0.5, p, power=0.95, n_max=200_000) for p in effects])
    fig, ax = plt.subplots()
    width = 0.4
    xs = np.arange(len(effects))
    ax.bar(xs - width / 2, ns_at_80, width=width, color=PALETTE["frequentist"], label="80% power")
    ax.bar(xs + width / 2, ns_at_95, width=width, color=PALETTE["bayesian"], label="95% power")
    ax.set_yscale("log")
    ax.set_xticks(xs)
    ax.set_xticklabels([f"effect to {p}" for p in effects])
    ax.set_ylabel("required N (log scale)")
    ax.set_title("Loop B: required N grows like 1/effect^2")
    ax.legend()
    for i, (a, b) in enumerate(zip(ns_at_80, ns_at_95)):
        ax.text(i - width / 2, a, f"{a:,}", ha="center", va="bottom", fontsize=8)
        ax.text(i + width / 2, b, f"{b:,}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    out = IMG_DIR / "required_n.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_mde_curve():
    apply_style()
    ns = np.unique(np.round(np.geomspace(50, 100_000, 80)).astype(int))
    e80 = np.array([mde(0.5, n=int(n), power=0.8) for n in ns])
    e95 = np.array([mde(0.5, n=int(n), power=0.95) for n in ns])
    fig, ax = plt.subplots()
    ax.plot(ns, e80, color=PALETTE["frequentist"], label="MDE at 80% power")
    ax.plot(ns, e95, color=PALETTE["bayesian"], label="MDE at 95% power")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("sample size N")
    ax.set_ylabel("minimum detectable effect")
    ax.set_title("Loop C: as N grows, the smallest detectable effect shrinks")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "mde_curve.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_bayesian_stopping(manifest):
    """Simulate a 'stop when CI is narrow enough' rule and compare to fixed-N frequentist."""
    apply_style()
    rng = np.random.default_rng(42)
    n_runs = 200
    target_width = 0.04  # require 95% credible interval width <= 0.04
    truth = 0.55
    stop_ns = []
    for _ in range(n_runs):
        # tossed seq, but evaluate posterior periodically for efficiency
        seq = rng.binomial(1, truth, size=20_000)
        cum = np.cumsum(seq)
        ns = np.arange(1, len(seq) + 1)
        # posterior is Beta(1+heads, 1+tails); width of 95% CI computable from beta ppf
        from scipy.stats import beta as beta_dist
        for n in ns[19::20]:  # check every 20 tosses to keep it fast
            heads = int(cum[n - 1])
            a, b = 1 + heads, 1 + (n - heads)
            lo = beta_dist.ppf(0.025, a, b)
            hi = beta_dist.ppf(0.975, a, b)
            if (hi - lo) <= target_width:
                stop_ns.append(int(n))
                break
        else:
            stop_ns.append(20_000)
    stop_ns = np.array(stop_ns)
    save_samples(stop_ns, DATA_DIR / "bayes_stopping_ns", seed=42, meta={"truth": truth, "target_ci_width": target_width, "n_runs": n_runs})

    # for comparison the frequentist 80%-power N for detecting 0.5 -> 0.55
    n_freq_80 = required_n(0.5, 0.55, power=0.8)

    fig, ax = plt.subplots()
    ax.hist(stop_ns, bins=30, color=PALETTE["bayesian"], alpha=0.75, label=f"Bayesian stopping N (median = {int(np.median(stop_ns))})")
    ax.axvline(n_freq_80, color=PALETTE["frequentist"], linestyle="--", linewidth=1.5, label=f"Frequentist 80%-power fixed N ({n_freq_80})")
    ax.set_xlabel("stopping N")
    ax.set_ylabel("number of runs")
    ax.set_title(f"Loop D: stopping when 95% CI width <= {target_width} (truth = {truth})")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "bayes_stopping.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_peeking_rejection():
    """Loop D edge case: peeking without alpha-spending inflates rejection rate.

    2,000 fair-coin runs of N = 1,000 tosses. After each toss (beyond a small
    warm-up) we check the two-sided z-test p-value and stop on the first
    p < 0.05. Plot the cumulative rejection rate as peeks accumulate and
    compare to the nominal alpha = 0.05 flat line.
    """
    apply_style()
    rng = np.random.default_rng(31337)
    n_runs = 2000
    n_tosses = 1000
    peek_every = 10
    alpha = 0.05

    # Precompute per-run heads trajectories, then scan peeks.
    seqs = rng.binomial(1, 0.5, size=(n_runs, n_tosses))
    cum = np.cumsum(seqs, axis=1)
    peek_ns = np.arange(peek_every, n_tosses + 1, peek_every)
    # Stopping time per run (or infinity if never crosses).
    stop_at = np.full(n_runs, np.inf)
    for n in peek_ns:
        heads = cum[:, n - 1]
        # Two-sided z-test against p=0.5.
        phat = heads / n
        se = np.sqrt(0.25 / n)
        z = np.abs(phat - 0.5) / se
        from scipy.stats import norm
        pvals = 2 * (1 - norm.cdf(z))
        mask = (pvals < alpha) & np.isinf(stop_at)
        stop_at[mask] = n
    rejected = np.isfinite(stop_at)
    # Cumulative rejection rate as a function of the peek horizon.
    cum_rej_rate = np.array([
        np.mean(stop_at <= n) for n in peek_ns
    ])

    fig, ax = plt.subplots()
    ax.plot(peek_ns, cum_rej_rate, color=PALETTE["frequentist"], linewidth=2,
            label=f"peek every {peek_every}, stop on first p < {alpha}")
    ax.axhline(alpha, color=PALETTE["muted"], linestyle="--", linewidth=1,
               label=f"nominal alpha = {alpha}")
    final = float(cum_rej_rate[-1])
    ax.annotate(f"after {n_tosses} tosses: {final:.2f}",
                xy=(n_tosses, final), xytext=(-90, -14),
                textcoords="offset points", fontsize=9)
    ax.set_xlabel("peek horizon (number of tosses seen so far)")
    ax.set_ylabel("cumulative rejection rate on fair coins")
    ax.set_ylim(0, max(0.4, final * 1.1))
    ax.set_title("Loop D edge case: peeking inflates the false-alarm rate")
    ax.legend(loc="lower right")
    fig.tight_layout()
    out = IMG_DIR / "peeking_rejection.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_power_curves(),
        render_required_n_table(),
        render_mde_curve(),
        render_bayesian_stopping(manifest),
        render_peeking_rejection(),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 3 figure: {p.name}")
    samples_path = DATA_DIR / "bayes_stopping_ns.npy"
    if samples_path.exists():
        add_artifact(manifest, path=samples_path, kind="samples", seed=42, sha256=_sha256_file(samples_path), description="Loop D: per-run Bayesian stopping N")

    save_manifest(manifest)
    print(f"Chapter 3: wrote {len(paths)} figures + 1 samples file")


if __name__ == "__main__":
    main()
