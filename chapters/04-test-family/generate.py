"""Regenerate Chapter 4 (the family of tests) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.inference.binomial import binom_test_exact  # noqa: E402
from expkit.inference.chi2 import goodness_of_fit  # noqa: E402
from expkit.inference.fisher import fisher_exact_2x2  # noqa: E402
from expkit.inference.normal import one_sample_z, one_sample_t  # noqa: E402
from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402

CHAPTER = "04-test-family"
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


def collect_pvalues(k: int, n: int) -> dict[str, float]:
    """Run all five tests against H0: p = 0.5 on the same observed (k, n)."""
    results = {}
    results["binomial exact"] = binom_test_exact(k, n).p_value
    results["normal-approx z"] = one_sample_z(k, n, p_null=0.5).p_value
    # chi-square goodness-of-fit on (k, n-k) vs (n/2, n/2)
    results["chi-square gof"] = goodness_of_fit(np.array([k, n - k]), expected_p=np.array([0.5, 0.5])).p_value
    # Fisher exact on observed vs an "ideal fair" reference of equal size
    fair_ref_heads = n // 2
    fair_ref_tails = n - fair_ref_heads
    table = np.array([[k, n - k], [fair_ref_heads, fair_ref_tails]])
    results["fisher exact (vs ideal)"] = fisher_exact_2x2(table).p_value
    # one-sample t on the 0/1 sequence (against mu_null = 0.5)
    seq = np.concatenate([np.ones(k), np.zeros(n - k)])
    results["one-sample t"] = one_sample_t(seq, mu_null=0.5).p_value
    return results


def render_pvalue_grid():
    """Five tests at three observed counts (60/100, 600/1000, 6000/10000) and one tiny case (6/10)."""
    apply_style()
    cases = [(6, 10), (60, 100), (600, 1000), (6000, 10000)]
    test_names = ["binomial exact", "normal-approx z", "chi-square gof", "fisher exact (vs ideal)", "one-sample t"]
    matrix = np.zeros((len(cases), len(test_names)))
    for i, (k, n) in enumerate(cases):
        res = collect_pvalues(k, n)
        for j, name in enumerate(test_names):
            matrix[i, j] = res[name]

    fig, ax = plt.subplots(figsize=(11, 4.5))
    width = 0.16
    xs = np.arange(len(cases))
    cmap = plt.get_cmap("viridis")
    for j, name in enumerate(test_names):
        ax.bar(xs + (j - 2) * width, matrix[:, j], width=width, color=cmap(j / max(1, len(test_names) - 1)), label=name)
    ax.axhline(0.05, color=PALETTE["muted"], linestyle="--", linewidth=1, label="alpha = 0.05")
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{k}/{n}" for k, n in cases])
    ax.set_ylabel("p-value")
    ax.set_yscale("log")
    ax.set_title("Loop A: five tests on the same data, four sample sizes")
    ax.legend(ncols=2, fontsize=9)
    fig.tight_layout()
    out = IMG_DIR / "pvalue_grid.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_normal_vs_exact_breakdown():
    """As N grows, when does normal-approx start to disagree with exact?"""
    apply_style()
    ns = [10, 25, 50, 100, 250, 500, 1000]
    rows = []
    for n in ns:
        for k in range(0, n + 1):
            ex = binom_test_exact(k, n).p_value
            z = one_sample_z(k, n).p_value
            if not np.isnan(z):
                rows.append((n, k, ex, z))
    arr = np.array(rows)

    # plot the ratio z/exact across the (n, k) plane near the boundary
    fig, ax = plt.subplots()
    for n in ns:
        rs = arr[arr[:, 0] == n]
        diffs = np.abs(rs[:, 3] - rs[:, 2])
        ax.plot(rs[:, 1] / n, diffs, label=f"N = {n}")
    ax.set_xlabel("observed fraction (k/n)")
    ax.set_ylabel("|p_z - p_exact|")
    ax.set_yscale("log")
    ax.set_xlim(0.0, 1.0)
    ax.set_title("Loop B: where normal-approx lies (small N) and where it doesn't (large N)")
    ax.legend(ncols=2, fontsize=9)
    fig.tight_layout()
    out = IMG_DIR / "normal_vs_exact.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_edge_cases():
    """Behaviour at extreme observations: 0/N, N/N, single toss."""
    apply_style()
    cases = [(0, 10), (10, 10), (1, 1), (0, 100), (100, 100)]
    test_names = ["binomial exact", "normal-approx z", "chi-square gof", "fisher exact (vs ideal)", "one-sample t"]
    out_text = []
    for k, n in cases:
        try:
            res = collect_pvalues(k, n)
        except Exception as e:  # pragma: no cover
            out_text.append(f"{k}/{n}: error -- {e}")
            continue
        out_text.append(f"{k}/{n}:  " + "  ".join(f"{name}={res[name]:.4g}" for name in test_names))

    fig, ax = plt.subplots(figsize=(11, 4.0))
    ax.axis("off")
    ax.text(0.0, 0.95, "\n".join(out_text), family="monospace", fontsize=9, va="top")
    ax.set_title("Loop C: edge cases. Note where t-test breaks (zero variance) and where normal-approx misbehaves.")
    fig.tight_layout()
    out = IMG_DIR / "edge_cases.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def fisher_reference_sweep(k: int = 60, n: int = 100, multipliers=(1, 10, 100, 10000)) -> list[tuple[int, float]]:
    """Show that Fisher (one-sample-misuse framing) converges to the exact binomial p-value
    as the idealized 50/50 reference grows. With reference size n it is conservative
    relative to exact; as the reference goes to infinity (50/50 treated as known) it
    matches the exact binomial test.
    """
    results = []
    exact_p = binom_test_exact(k, n).p_value
    for m in multipliers:
        rn = n * m
        rh = rn // 2
        rt = rn - rh
        table = np.array([[k, n - k], [rh, rt]])
        p = fisher_exact_2x2(table).p_value
        results.append((rn, p))
    print(f"Fisher convergence at {k}/{n} (exact binomial p = {exact_p:.4f}):")
    for rn, p in results:
        print(f"  reference size {rn}: Fisher p = {p:.4f}")
    return results


def render_bayes_alongside_frequentist():
    """For each scenario in Loop A, also show the Beta-binomial conjugate posterior summary."""
    apply_style()
    from scipy.stats import beta as beta_dist
    cases = [(6, 10), (60, 100), (600, 1000), (6000, 10000)]
    fig, axes = plt.subplots(1, len(cases), figsize=(13, 3.6), sharey=True)
    ps = np.linspace(0, 1, 1000)
    for ax, (k, n) in zip(axes, cases):
        post_a, post_b = 1 + k, 1 + (n - k)
        ax.plot(ps, beta_dist.pdf(ps, post_a, post_b), color=PALETTE["bayesian"])
        ax.axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1)
        # 95% credible interval shaded
        lo = beta_dist.ppf(0.025, post_a, post_b)
        hi = beta_dist.ppf(0.975, post_a, post_b)
        ax.axvspan(lo, hi, color=PALETTE["bayesian"], alpha=0.15)
        ax.set_title(f"{k}/{n}\nBeta({post_a},{post_b})")
        ax.set_xlim(0, 1)
        ax.set_xlabel("p")
    axes[0].set_ylabel("posterior density")
    fig.suptitle("Loop D: Bayesian view of the same data (flat prior + observed)")
    fig.tight_layout()
    out = IMG_DIR / "bayes_alongside.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_pvalue_grid(),
        render_normal_vs_exact_breakdown(),
        render_edge_cases(),
        render_bayes_alongside_frequentist(),
    ]
    fisher_reference_sweep()
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 4 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 4: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
