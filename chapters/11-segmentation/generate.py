"""Regenerate Chapter 11 (segmentation done right) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.inference.bayes import hierarchical_segmented_posterior  # noqa: E402
from expkit.inference.cmh import cochran_mantel_haenszel  # noqa: E402
from expkit.inference.multitest import benjamini_hochberg, bonferroni, holm  # noqa: E402
from expkit.inference.normal import two_proportion_z  # noqa: E402
from expkit.io.samples import _sha256_file, save_idata, save_samples  # noqa: E402
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.segments.behavioral import simulate_population, BEHAVIORAL_LABELS  # noqa: E402

CHAPTER = "11-segmentation"
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


def render_demographic_vs_behavioral(manifest):
    """Same population. Slice by demographics (no signal) vs behavioural (huge differences)."""
    apply_style()
    rng = np.random.default_rng(110)
    n = 5000
    df = simulate_population(n, seed=110)
    # Add a fake demographic that we'll show is uninformative.
    df["country"] = rng.choice(["A", "B", "C"], size=n)
    df["age"] = rng.integers(18, 65, size=n)
    # Treatment effect is heterogeneous by behavioural segment, NOT by demographics.
    treatment_lift_by_segment = {"active_contributor": 0.10, "active_consumer": 0.04, "silent_intentional": -0.03, "passive_consumer": 0.0}
    df["arm"] = rng.choice(["control", "treatment"], size=n)
    base_p = 0.30
    df["outcome"] = 0
    for seg, lift in treatment_lift_by_segment.items():
        for arm in ["control", "treatment"]:
            mask = (df["segment"] == seg) & (df["arm"] == arm)
            p = base_p + (lift if arm == "treatment" else 0.0)
            df.loc[mask, "outcome"] = rng.binomial(1, max(0, min(1, p)), size=int(mask.sum()))

    # Demographic slice: by country
    by_country = df.groupby(["country", "arm"])["outcome"].mean().unstack()
    country_lifts = by_country["treatment"] - by_country["control"]
    # Behavioural slice
    by_segment = df.groupby(["segment", "arm"])["outcome"].mean().unstack()
    segment_lifts = by_segment["treatment"] - by_segment["control"]
    # Aggregate
    pooled = df.groupby("arm")["outcome"].mean()
    pooled_lift = pooled["treatment"] - pooled["control"]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0), sharey=True)
    cmap = plt.get_cmap("viridis")
    axes[0].bar(country_lifts.index, country_lifts.values, color=[cmap(i / max(1, len(country_lifts) - 1)) for i in range(len(country_lifts))])
    axes[0].axhline(pooled_lift, color=PALETTE["bayesian"], linestyle=":", linewidth=1, label=f"pooled lift = {pooled_lift:+.3f}")
    axes[0].axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[0].set_title("By demographic slice (country)")
    axes[0].set_ylabel("treatment - control")
    axes[0].legend()
    axes[1].bar(segment_lifts.index, segment_lifts.values, color=[cmap(i / max(1, len(segment_lifts) - 1)) for i in range(len(segment_lifts))])
    axes[1].axhline(pooled_lift, color=PALETTE["bayesian"], linestyle=":", linewidth=1, label=f"pooled lift = {pooled_lift:+.3f}")
    axes[1].axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    axes[1].set_title("By behavioural segment")
    axes[1].legend()
    plt.setp(axes[1].get_xticklabels(), rotation=15, fontsize=8)
    fig.suptitle("Loop A: demographic slicing is flat. Behavioural slicing reveals hetero effects.")
    fig.tight_layout()
    out = IMG_DIR / "demographic_vs_behavioral.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_segment_signature():
    """Show the three behavioural axes for each segment."""
    apply_style()
    df = simulate_population(5000, seed=111)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5), sharey=False)
    for ax, col in zip(axes, ["weekly_active_rate", "contribution_rate", "intentional_rate"]):
        for label in BEHAVIORAL_LABELS:
            sub = df[df["segment"] == label][col]
            ax.hist(sub, bins=30, alpha=0.5, label=label)
        ax.set_xlabel(col)
        ax.legend(fontsize=7)
    fig.suptitle("Loop B: each behavioural segment has a distinctive signature on the three axes")
    fig.tight_layout()
    out = IMG_DIR / "segment_signature.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_segmentation_choices():
    """Three different segmentation schemes on the same population, showing they tell different stories."""
    apply_style()
    rng = np.random.default_rng(112)
    n = 4000
    df = simulate_population(n, seed=112)
    # Three segmentation schemes:
    # 1. Tenure (synthetic, simple) -- recently joined vs veteran
    df["tenure_days"] = rng.integers(0, 800, size=n)
    df["tenure_seg"] = np.where(df["tenure_days"] < 90, "new", "veteran")
    # 2. Activity tertile
    df["activity_seg"] = pd.qcut(df["weekly_active_rate"], q=3, labels=["low_active", "med_active", "high_active"])
    # 3. Behavioural label (already defined)
    # Apply a treatment that helps high-active, hurts low-active, neutral middle.
    df["arm"] = rng.choice(["control", "treatment"], size=n)
    base_p = 0.20
    df["outcome"] = rng.binomial(1, base_p, n)
    # Inject heterogeneity tied to weekly_active_rate
    treat_mask = df["arm"] == "treatment"
    new_p = np.clip(base_p + (df.loc[treat_mask, "weekly_active_rate"] - 0.4) * 0.3, 0.0, 1.0)
    df.loc[treat_mask, "outcome"] = rng.binomial(1, new_p)

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
    for ax, scheme, title in zip(
        axes,
        ["tenure_seg", "activity_seg", "segment"],
        ["Tenure (new vs veteran)", "Activity tertile", "Behavioural label"],
    ):
        diffs = df.groupby([scheme, "arm"])["outcome"].mean().unstack()
        lifts = diffs["treatment"] - diffs["control"]
        ax.bar(lifts.index.astype(str), lifts.values, color=plt.get_cmap("viridis")(np.linspace(0, 1, len(lifts))))
        ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
        ax.set_title(title)
        ax.set_ylabel("lift")
        plt.setp(ax.get_xticklabels(), rotation=15, fontsize=8)
    fig.suptitle("Loop C: same data, three segmentation schemes, three stories")
    fig.tight_layout()
    out = IMG_DIR / "segmentation_choices.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_multiplicity(manifest):
    """Loop C.5: per-segment z-tests with Bonferroni / Holm / BH adjustment, plus CMH.

    Reuses the seed-110, n=5000 design from Loop A so the numbers in the
    chapter prose are reproducible. Saves a CSV-style sidecar of (segment,
    raw_p, bonferroni, holm, bh) plus the CMH summary so downstream prose can
    cite specific values from data/multiplicity.npy.
    """
    apply_style()
    rng = np.random.default_rng(110)
    n = 5000
    df = simulate_population(n, seed=110)
    treat_lift = {"active_contributor": 0.10, "active_consumer": 0.04, "silent_intentional": -0.03, "passive_consumer": 0.0}
    df["arm"] = rng.choice(["control", "treatment"], size=n)
    base_p = 0.30
    df["outcome"] = 0
    for seg, lift in treat_lift.items():
        for arm_name in ["control", "treatment"]:
            mask = (df["segment"] == seg) & (df["arm"] == arm_name)
            p = base_p + (lift if arm_name == "treatment" else 0.0)
            df.loc[mask, "outcome"] = rng.binomial(1, max(0, min(1, p)), size=int(mask.sum()))

    segments = sorted(df["segment"].unique())
    raw_p = []
    tables = []  # for CMH: each stratum is [[a=t_succ, b=t_fail], [c=c_succ, d=c_fail]]
    rows = []
    for seg in segments:
        sub = df[df["segment"] == seg]
        c = sub[sub["arm"] == "control"]
        t = sub[sub["arm"] == "treatment"]
        s_c, n_c = int(c["outcome"].sum()), len(c)
        s_t, n_t = int(t["outcome"].sum()), len(t)
        res = two_proportion_z(s_t, n_t, s_c, n_c, alternative="two-sided")
        raw_p.append(res.p_value)
        rows.append({"segment": seg, "n_c": n_c, "s_c": s_c, "n_t": n_t, "s_t": s_t, "raw_p": res.p_value})
        tables.append([[s_t, n_t - s_t], [s_c, n_c - s_c]])
    raw_p = np.array(raw_p)

    bonf = bonferroni(raw_p)
    h = holm(raw_p)
    bh = benjamini_hochberg(raw_p)
    cmh = cochran_mantel_haenszel(np.array(tables, dtype=float))

    # Save sidecar of numbers so chapter prose / notebook can cite exact values.
    arr = np.column_stack([raw_p, bonf.adjusted_p, h.adjusted_p, bh.adjusted_p])
    res = save_samples(
        arr,
        DATA_DIR / "multiplicity",
        seed=110,
        meta={
            "columns": ["raw_p", "bonferroni", "holm", "bh"],
            "segments": list(segments),
            "n_per_segment": {seg: {"control": rows[i]["n_c"], "treatment": rows[i]["n_t"]} for i, seg in enumerate(segments)},
            "successes_per_segment": {seg: {"control": rows[i]["s_c"], "treatment": rows[i]["s_t"]} for i, seg in enumerate(segments)},
            "cmh": {
                "statistic": cmh.statistic,
                "p_value": cmh.p_value,
                "common_odds_ratio": cmh.common_odds_ratio,
                "log_or": cmh.log_or,
                "log_or_se": cmh.log_or_se,
                "n_strata": cmh.n_strata,
            },
            "alpha": 0.05,
            "true_lifts": treat_lift,
        },
    )
    add_artifact(
        manifest, path=res.path, kind="samples", seed=110, sha256=res.sha256,
        description="Loop C.5: per-segment raw p plus Bonferroni / Holm / BH and CMH on the same 4-stratum table",
    )

    # Plot raw vs three corrections side by side, with alpha=0.05 line.
    fig, ax = plt.subplots(figsize=(10, 4.5))
    x = np.arange(len(segments))
    width = 0.2
    ax.bar(x - 1.5 * width, raw_p, width, label="raw p", color=PALETTE["frequentist"])
    ax.bar(x - 0.5 * width, bonf.adjusted_p, width, label="Bonferroni", color=PALETTE["highlight"])
    ax.bar(x + 0.5 * width, h.adjusted_p, width, label="Holm", color=PALETTE["bayesian"])
    ax.bar(x + 1.5 * width, bh.adjusted_p, width, label="BH (FDR)", color=PALETTE["muted"])
    ax.axhline(0.05, color="black", linestyle="--", linewidth=1, label="alpha = 0.05")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(segments, rotation=15, fontsize=8)
    ax.set_ylabel("p-value (log scale)")
    ax.set_title(
        f"Loop C.5: per-segment p-values vs Bonferroni / Holm / BH. "
        f"CMH chi2={cmh.statistic:.1f}, p={cmh.p_value:.2e}, OR_MH={cmh.common_odds_ratio:.2f}"
    )
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    out = IMG_DIR / "multiplicity.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_hierarchical_pymc(manifest):
    """Hierarchical Bayesian model on segmented A/B data.

    Per-segment treatment effect drawn from a population-level distribution.
    The model partial-pools small segments toward the population mean.
    """
    apply_style()
    rng = np.random.default_rng(115)
    n_total = 4000
    df = simulate_population(n_total, seed=115)
    df["arm"] = rng.choice(["control", "treatment"], size=n_total)
    treat_lift = {"active_contributor": 0.10, "active_consumer": 0.04, "silent_intentional": -0.03, "passive_consumer": 0.0}
    df["outcome"] = 0
    base = 0.30
    for seg, lift in treat_lift.items():
        for arm_name in ["control", "treatment"]:
            m = (df["segment"] == seg) & (df["arm"] == arm_name)
            p = base + (lift if arm_name == "treatment" else 0.0)
            df.loc[m, "outcome"] = rng.binomial(1, max(0, min(1, p)), size=int(m.sum()))

    successes_by_segment = {}
    n_by_segment = {}
    for seg in sorted(df["segment"].unique()):
        sub = df[df["segment"] == seg]
        successes_by_segment[seg] = {
            "control": int(sub[sub["arm"] == "control"]["outcome"].sum()),
            "treatment": int(sub[sub["arm"] == "treatment"]["outcome"].sum()),
        }
        n_by_segment[seg] = {
            "control": int((sub["arm"] == "control").sum()),
            "treatment": int((sub["arm"] == "treatment").sum()),
        }

    idata = hierarchical_segmented_posterior(
        successes_by_segment, n_by_segment,
        seed=1115, draws=1500, chains=2, tune=1500, progressbar=False,
    )
    res = save_idata(idata, DATA_DIR / "hierarchical_posterior", seed=1115, meta={
        "n_total": n_total,
        "treat_lift": treat_lift,
        "model": "logit baseline + Normal effect per segment, with population-level Normal(mu, tau)",
    })
    add_artifact(manifest, path=res.path, kind="idata", seed=1115, sha256=res.sha256, description="Hierarchical Bayesian model on segmented A/B data")

    # Per-segment effect posteriors on the probability scale
    p_t = idata.posterior["p_treatment"].values  # (chain, draw, segment)
    p_c = idata.posterior["p_control"].values
    diff = p_t - p_c
    segments = list(idata.posterior.coords["segment"].values)

    # Independent (no-pooling) per-segment estimates for comparison
    independent_diffs = {}
    for seg in segments:
        s = successes_by_segment[seg]; n_ = n_by_segment[seg]
        independent_diffs[seg] = (s["treatment"] / n_["treatment"]) - (s["control"] / n_["control"])

    fig, ax = plt.subplots(figsize=(10, 4.5))
    cmap = plt.get_cmap("viridis")
    xs = np.arange(len(segments))
    for i, seg in enumerate(segments):
        d = diff[:, :, i].ravel()
        lo, hi = float(np.quantile(d, 0.025)), float(np.quantile(d, 0.975))
        mean = float(np.mean(d))
        ax.errorbar(i - 0.15, mean, yerr=[[mean - lo], [hi - mean]], fmt="o", color=cmap(i / max(1, len(segments) - 1)), capsize=4, markersize=8, label=f"{seg} (Bayesian)" if i == 0 else None)
        ax.scatter(i + 0.15, independent_diffs[seg], color=PALETTE["highlight"], marker="s", s=60, zorder=5, label="independent (no pool)" if i == 0 else None)
        ax.axhline(treat_lift[seg], xmin=(i - 0.4) / len(segments) + 0.03, xmax=(i + 0.4) / len(segments) - 0.03,
                   color=PALETTE["muted"], linestyle=":", linewidth=1)
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_xticks(xs)
    ax.set_xticklabels(segments, rotation=15, fontsize=8)
    ax.set_ylabel("treatment - control")
    ax.set_title("Loop D: hierarchical Bayesian per-segment effects vs independent estimates (true effect = dotted)")
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    out = IMG_DIR / "hierarchical_effects.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_demographic_vs_behavioral(manifest),
        render_segment_signature(),
        render_segmentation_choices(),
        render_multiplicity(manifest),
        render_hierarchical_pymc(manifest),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 11 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 11: wrote {len(paths)} figures + 1 PyMC trace")


if __name__ == "__main__":
    main()
