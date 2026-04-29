"""Regenerate Chapter 1 datasets and images from fixed seeds.

Run from the repo root:

    python chapters/01-the-coin/generate.py

Produces, under ``chapters/01-the-coin/data/`` and ``chapters/01-the-coin/images/``:
  - small toss sequences (3-toss, 10-toss, multiple seeds)
  - long sequences (N=10, 100, 1000, 10000)
  - PyMC InferenceData snapshots at N=10, 100, 1000, 10000
  - running-fraction plots, the multi-seed-at-N=10 panel, the 0.5-vs-0.55
    overlap, and the posterior-tightening sequence

Also updates the cross-cutting ``data/manifest.yaml`` with one entry per file.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.inference.bayes import coin_posterior  # noqa: E402
from expkit.inference.binomial import wilson_ci  # noqa: E402
from expkit.io.samples import save_idata, save_samples  # noqa: E402
from expkit.plot.diagnostic import (  # noqa: E402
    plot_posterior_sequence,
    plot_running_fraction,
    plot_running_fraction_with_band,
)
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.sim.coin import bernoulli_sequence, running_fraction  # noqa: E402

CHAPTER_DIR = Path(__file__).resolve().parent
DATA_DIR = CHAPTER_DIR / "data"
IMG_DIR = CHAPTER_DIR / "images"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.yaml"

# Reproducibility seeds. Pinned so that re-running this script byte-identical
# regenerates every artifact.
SEEDS = {
    # First-three seed 4 yields HHH (the dramatic opener); next-seven seed 2
    # brings the 10-toss tally to 6 heads, a borderline-ambiguous result.
    "loop_a_first_three": 4,
    "loop_a_next_seven": 2,
    "loop_b_seeds": [101, 102, 103, 104, 105, 106],
    "loop_c_long": 7,
    "loop_d_fair": 21,
    "loop_d_biased": 22,
    "pymc": 999,
}

# Sample sizes used for the posterior-tightening sequence.
TIGHTENING_NS = [10, 100, 1000, 10000]


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return yaml.safe_load(MANIFEST_PATH.read_text()) or {"artifacts": []}
    return {"artifacts": []}


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(yaml.safe_dump(manifest, sort_keys=False))


def add_artifact(
    manifest: dict,
    *,
    path: Path,
    chapter: str,
    kind: str,
    seed: int | str,
    sha256: str,
    description: str,
) -> None:
    rel = str(path.relative_to(REPO_ROOT))
    manifest["artifacts"] = [a for a in manifest["artifacts"] if a.get("path") != rel]
    manifest["artifacts"].append(
        {
            "path": rel,
            "chapter": chapter,
            "kind": kind,
            "seed": seed,
            "sha256": sha256,
            "description": description,
        }
    )


def loop_a_three_then_ten(manifest: dict) -> dict[str, np.ndarray]:
    """Loop A: 3 tosses then 10 tosses, recorded with seeds."""
    first_three = bernoulli_sequence(3, p=0.5, seed=SEEDS["loop_a_first_three"])
    next_seven = bernoulli_sequence(7, p=0.5, seed=SEEDS["loop_a_next_seven"])
    ten = np.concatenate([first_three, next_seven])

    res_a = save_samples(first_three, DATA_DIR / "loop_a_first_three", seed=SEEDS["loop_a_first_three"], meta={"p": 0.5})
    res_b = save_samples(next_seven, DATA_DIR / "loop_a_next_seven", seed=SEEDS["loop_a_next_seven"], meta={"p": 0.5})
    res_c = save_samples(ten, DATA_DIR / "loop_a_ten", seed=f"{SEEDS['loop_a_first_three']}+{SEEDS['loop_a_next_seven']}", meta={"p": 0.5})

    for res, descr, seed in (
        (res_a, "Loop A: first three tosses (HHH chosen seed)", SEEDS["loop_a_first_three"]),
        (res_b, "Loop A: next seven tosses", SEEDS["loop_a_next_seven"]),
        (res_c, "Loop A: combined 10-toss sequence", f"{SEEDS['loop_a_first_three']}+{SEEDS['loop_a_next_seven']}"),
    ):
        add_artifact(
            manifest,
            path=res.path,
            chapter="01-the-coin",
            kind="samples",
            seed=seed,
            sha256=res.sha256,
            description=descr,
        )

    return {"first_three": first_three, "next_seven": next_seven, "ten": ten}


def loop_b_many_seeds(manifest: dict) -> list[np.ndarray]:
    """Loop B: 100 tosses, several seeds. Saved together as one stacked array."""
    seqs = [bernoulli_sequence(100, p=0.5, seed=s) for s in SEEDS["loop_b_seeds"]]
    stacked = np.stack(seqs)
    res = save_samples(
        stacked,
        DATA_DIR / "loop_b_n100_six_seeds",
        seed=str(SEEDS["loop_b_seeds"]),
        meta={"p": 0.5, "n_per_seed": 100, "seeds": SEEDS["loop_b_seeds"]},
    )
    add_artifact(
        manifest,
        path=res.path,
        chapter="01-the-coin",
        kind="samples",
        seed=str(SEEDS["loop_b_seeds"]),
        sha256=res.sha256,
        description="Loop B: six 100-toss fair-coin sequences",
    )
    return seqs


def loop_c_long(manifest: dict) -> np.ndarray:
    """Loop C: a single 10,000-toss fair sequence; subsets at 100 and 1000 are slices."""
    long = bernoulli_sequence(10_000, p=0.5, seed=SEEDS["loop_c_long"])
    res = save_samples(
        long,
        DATA_DIR / "loop_c_n10000",
        seed=SEEDS["loop_c_long"],
        meta={"p": 0.5, "n": 10_000},
    )
    add_artifact(
        manifest,
        path=res.path,
        chapter="01-the-coin",
        kind="samples",
        seed=SEEDS["loop_c_long"],
        sha256=res.sha256,
        description="Loop C: 10,000-toss fair-coin sequence",
    )
    return long


def loop_d_fair_vs_biased(manifest: dict) -> tuple[np.ndarray, np.ndarray]:
    fair = bernoulli_sequence(2000, p=0.5, seed=SEEDS["loop_d_fair"])
    biased = bernoulli_sequence(2000, p=0.55, seed=SEEDS["loop_d_biased"])
    res_f = save_samples(fair, DATA_DIR / "loop_d_fair", seed=SEEDS["loop_d_fair"], meta={"p": 0.5, "n": 2000})
    res_b = save_samples(biased, DATA_DIR / "loop_d_biased", seed=SEEDS["loop_d_biased"], meta={"p": 0.55, "n": 2000})
    add_artifact(
        manifest,
        path=res_f.path,
        chapter="01-the-coin",
        kind="samples",
        seed=SEEDS["loop_d_fair"],
        sha256=res_f.sha256,
        description="Loop D: 2,000-toss fair-coin sequence (p=0.50)",
    )
    add_artifact(
        manifest,
        path=res_b.path,
        chapter="01-the-coin",
        kind="samples",
        seed=SEEDS["loop_d_biased"],
        sha256=res_b.sha256,
        description="Loop D: 2,000-toss slightly-biased sequence (p=0.55)",
    )
    return fair, biased


def fit_pymc_snapshots(long_seq: np.ndarray, manifest: dict):
    """Fit a PyMC posterior on prefixes of ``long_seq`` of varying length."""
    snapshots = []
    for n in TIGHTENING_NS:
        idata = coin_posterior(
            long_seq[:n],
            seed=SEEDS["pymc"] + n,
            draws=1500,
            chains=2,
            tune=1000,
            progressbar=False,
        )
        path = DATA_DIR / f"posterior_n{n}"
        res = save_idata(
            idata,
            path,
            seed=SEEDS["pymc"] + n,
            meta={"prefix_n": n, "true_p": 0.5, "model": "Bernoulli with Beta(1,1) prior"},
        )
        add_artifact(
            manifest,
            path=res.path,
            chapter="01-the-coin",
            kind="idata",
            seed=SEEDS["pymc"] + n,
            sha256=res.sha256,
            description=f"PyMC posterior on p after N={n} fair-coin tosses",
        )
        snapshots.append(idata)
    return snapshots


def render_loop_a_image(seqs: dict[str, np.ndarray]) -> Path:
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    plot_running_fraction(seqs["first_three"], ax=axes[0], color=PALETTE["frequentist"])
    axes[0].set_title("first 3 tosses")
    plot_running_fraction(seqs["ten"], ax=axes[1], color=PALETTE["frequentist"])
    axes[1].set_title("after 10 tosses")
    fig.suptitle("Loop A: a tiny coin experiment", fontsize=12)
    fig.tight_layout()
    out = IMG_DIR / "loop_a_three_then_ten.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_loop_b_image(seqs: list[np.ndarray]) -> Path:
    apply_style()
    fig, ax = plt.subplots()
    cmap = plt.get_cmap("viridis")
    for i, s in enumerate(seqs):
        ax.plot(np.arange(1, len(s) + 1), running_fraction(s), color=cmap(i / max(1, len(seqs) - 1)), alpha=0.85, label=f"seed {SEEDS['loop_b_seeds'][i]}")
    ax.axhline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1, label="true p = 0.50")
    ax.set_xlabel("toss number")
    ax.set_ylabel("running fraction of heads")
    ax.set_ylim(0.0, 1.0)
    ax.set_title("Loop B: six fair-coin runs of 100 tosses each")
    ax.legend(ncols=2, loc="best")
    fig.tight_layout()
    out = IMG_DIR / "loop_b_six_runs_n100.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_loop_c_panels(long_seq: np.ndarray) -> Path:
    apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.5))
    for ax, n in zip(axes.flat, [10, 100, 1000, 10000]):
        plot_running_fraction_with_band(long_seq[:n], ax=ax, alpha=0.05, color=PALETTE["frequentist"])
        ax.set_title(f"after N = {n} tosses")
    fig.suptitle("Loop C: the running fraction settles, the Wilson band shrinks", fontsize=12)
    fig.tight_layout()
    out = IMG_DIR / "loop_c_running_fraction_grid.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_loop_d_overlap(fair: np.ndarray, biased: np.ndarray) -> Path:
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

    # Left: running fractions side by side.
    axes[0].plot(np.arange(1, len(fair) + 1), running_fraction(fair), color=PALETTE["frequentist"], label="fair (p = 0.50)")
    axes[0].plot(np.arange(1, len(biased) + 1), running_fraction(biased), color=PALETTE["bayesian"], label="biased (p = 0.55)")
    axes[0].axhline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[0].axhline(0.55, color=PALETTE["muted"], linestyle=":", linewidth=1)
    axes[0].set_xlabel("toss number")
    axes[0].set_ylabel("running fraction of heads")
    axes[0].set_ylim(0.4, 0.7)
    axes[0].set_xscale("log")
    axes[0].set_title("running fractions")
    axes[0].legend(loc="best")

    # Right: histogram of head counts in N=10 batches drawn from each coin.
    rng = np.random.default_rng(0)
    fair_counts = rng.binomial(10, 0.5, size=20000)
    biased_counts = rng.binomial(10, 0.55, size=20000)
    bins = np.arange(-0.5, 11.5, 1.0)
    axes[1].hist(fair_counts, bins=bins, density=True, alpha=0.55, color=PALETTE["frequentist"], label="fair")
    axes[1].hist(biased_counts, bins=bins, density=True, alpha=0.55, color=PALETTE["bayesian"], label="biased")
    axes[1].set_xlabel("heads in 10 tosses")
    axes[1].set_ylabel("frequency")
    axes[1].set_title("heads-in-10 distributions overlap")
    axes[1].legend(loc="best")

    fig.tight_layout()
    out = IMG_DIR / "loop_d_fair_vs_biased.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_posterior_tightening(snapshots) -> Path:
    apply_style()
    fig, ax = plt.subplots()
    plot_posterior_sequence(snapshots, TIGHTENING_NS, ax=ax, truth=0.5)
    ax.set_title("Bayesian view: the posterior tightens around p = 0.5")
    fig.tight_layout()
    out = IMG_DIR / "posterior_tightening.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_two_lens_endcap(long_seq: np.ndarray, snapshots) -> Path:
    """Frequentist Wilson CI vs Bayesian credible interval at the same Ns."""
    apply_style()
    fig, ax = plt.subplots()
    fair_idata = snapshots
    cred_centers = []
    cred_los = []
    cred_his = []
    wilson_centers = []
    wilson_los = []
    wilson_his = []
    for n, idata in zip(TIGHTENING_NS, fair_idata):
        prefix = long_seq[:n]
        k = int(prefix.sum())
        wilson_centers.append(k / n)
        lo, hi = wilson_ci(k, n)
        wilson_los.append(lo)
        wilson_his.append(hi)

        p_samples = idata.posterior["p"].values.ravel()
        cred_centers.append(float(np.mean(p_samples)))
        cred_los.append(float(np.quantile(p_samples, 0.025)))
        cred_his.append(float(np.quantile(p_samples, 0.975)))

    xs = np.arange(len(TIGHTENING_NS))
    width = 0.18
    ax.errorbar(
        xs - width,
        wilson_centers,
        yerr=[np.array(wilson_centers) - np.array(wilson_los), np.array(wilson_his) - np.array(wilson_centers)],
        fmt="o",
        color=PALETTE["frequentist"],
        capsize=4,
        label="Wilson 95% CI (frequentist)",
    )
    ax.errorbar(
        xs + width,
        cred_centers,
        yerr=[np.array(cred_centers) - np.array(cred_los), np.array(cred_his) - np.array(cred_centers)],
        fmt="s",
        color=PALETTE["bayesian"],
        capsize=4,
        label="95% credible interval (Bayesian)",
    )
    ax.axhline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1, label="true p = 0.50")
    ax.set_xticks(xs)
    ax.set_xticklabels([f"N = {n}" for n in TIGHTENING_NS])
    ax.set_ylabel("p")
    ax.set_ylim(0.3, 0.7)
    ax.set_title("Two-lens endcap: frequentist CI vs Bayesian credible interval")
    ax.legend(loc="best")
    fig.tight_layout()
    out = IMG_DIR / "two_lens_endcap.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main() -> None:
    ensure_dirs()
    manifest = load_manifest()

    seqs_a = loop_a_three_then_ten(manifest)
    seqs_b = loop_b_many_seeds(manifest)
    long_seq = loop_c_long(manifest)
    fair, biased = loop_d_fair_vs_biased(manifest)
    snapshots = fit_pymc_snapshots(long_seq, manifest)

    paths = [
        render_loop_a_image(seqs_a),
        render_loop_b_image(seqs_b),
        render_loop_c_panels(long_seq),
        render_loop_d_overlap(fair, biased),
        render_posterior_tightening(snapshots),
        render_two_lens_endcap(long_seq, snapshots),
    ]
    for p in paths:
        # Images are derived artifacts; record them with a short description but no seed.
        from expkit.io.samples import _sha256_file  # local import to avoid noise

        add_artifact(
            manifest,
            path=p,
            chapter="01-the-coin",
            kind="image",
            seed="derived",
            sha256=_sha256_file(p),
            description=f"Chapter 1 figure: {p.name}",
        )

    save_manifest(manifest)
    print(f"Chapter 1: wrote {len(manifest['artifacts'])} manifest entries; "
          f"{len(paths)} figures under {IMG_DIR.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
