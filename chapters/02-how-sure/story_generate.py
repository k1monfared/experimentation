"""Regenerate Chapter 2 (How sure am I, really) story-track figures.

Six figures, all written to ``images/story/`` and tracked in
``data/manifest.yaml``. Designed for the prose to do the work of a
caption: each chart is small, focused, and only shows what the
narrative needs at that moment.
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
from expkit.plot.story import (  # noqa: E402
    PALETTE, apply_story_style, reference_line,
)

CHAPTER = "02-how-sure"
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


# Common helper: histogram of binomial(N, 0.5) over k=0..N.
def _binom_pmf(n, p=0.5):
    ks = np.arange(0, n + 1)
    return ks, stats.binom.pmf(ks, n, p)


def render_ten_thousand_people_raw():
    """Raw-count histogram: 10,000 people each tossing a fair coin 100 times.

    A few specific bars are annotated so the reader can build the chart in
    their head before seeing the full thing.
    """
    apply_story_style()
    n = 100
    ks, pmf = _binom_pmf(n)
    counts = np.round(pmf * 10000).astype(int)

    fig, ax = plt.subplots(figsize=(11, 4.6))
    bars_ = ax.bar(ks, counts, color=PALETTE["soft"], width=0.85, edgecolor=PALETTE["muted"], linewidth=0.4)
    # Highlight a few bars in focus color and annotate them with their count.
    highlights = {50: counts[50], 60: counts[60], 65: counts[65], 35: counts[35]}
    for k in highlights:
        bars_[k].set_color(PALETTE["focus"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, counts.max() * 1.30)
    ax.set_xlabel("number of heads (out of 100 tosses)")
    ax.set_ylabel("how many of the 10,000 people landed there")

    # Annotations
    annotations = [
        (50, counts[50], f"about {counts[50]} people\ngot exactly 50 heads"),
        (60, counts[60], f"about {counts[60]} got 60"),
        (65, counts[65], f"about {counts[65]} got 65"),
        (35, counts[35], f"about {counts[35]} got 35"),
    ]
    for k, h, text in annotations:
        ax.annotate(
            text,
            xy=(k, h),
            xytext=(k - 5 if k < 50 else k + 5, h + counts.max() * 0.18),
            fontsize=9, ha="center", color=PALETTE["ink"],
            arrowprops=dict(arrowstyle="-", color=PALETTE["muted"], lw=0.7),
        )
    out = IMG_DIR / "ten_thousand_people.png"
    fig.savefig(out)
    plt.close(fig)
    return out, counts


def render_what_would_I_see_if_fair():
    """Same histogram, but with percentages on the y-axis. Shape identical."""
    apply_story_style()
    n = 100
    ks, pmf = _binom_pmf(n)
    pct = pmf * 100  # convert to percentage
    fig, ax = plt.subplots(figsize=(10, 4.0))
    ax.bar(ks, pct, color=PALETTE["focus"], width=0.85)
    ax.set_xlabel("number of heads (out of 100 tosses)")
    ax.set_ylabel("percent of the 10,000 people who landed there")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, pct.max() * 1.08)
    out = IMG_DIR / "what_would_I_see_if_fair.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def _symmetric_surprise_zone(n, pmf, threshold):
    """Largest symmetric two-tailed rejection region with total mass <= threshold."""
    tails = set()
    cum = 0.0
    for k in range(n // 2 + 1):
        j = n - k
        add = pmf[k] + (pmf[j] if k != j else 0.0)
        if cum + add > threshold:
            break
        tails.add(int(k))
        if j != k:
            tails.add(int(j))
        cum += add
    return tails, cum


def render_surprise_tails():
    """Same histogram, but with the two-sided 5% tails highlighted."""
    apply_story_style()
    n = 100
    ks, pmf = _binom_pmf(n)
    threshold = 0.05
    tails, cum = _symmetric_surprise_zone(n, pmf, threshold)
    colors = [PALETTE["contrast"] if k in tails else PALETTE["focus"] for k in ks]
    fig, ax = plt.subplots(figsize=(10, 4.0))
    ax.bar(ks, pmf, color=colors, width=0.85)
    ax.set_xlabel("number of heads in 100 tosses")
    ax.set_ylabel("how often this would happen with a fair coin")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, max(pmf) * 1.08)
    out = IMG_DIR / "surprise_tails.png"
    fig.savefig(out)
    plt.close(fig)
    # Compute the cutoffs for the prose
    in_tails = sorted(tails)
    lo_cut = max(k for k in in_tails if k < n // 2) if any(k < n // 2 for k in in_tails) else None
    hi_cut = min(k for k in in_tails if k > n // 2) if any(k > n // 2 for k in in_tails) else None
    return out, lo_cut, hi_cut, cum


def render_my_observations_on_the_chart():
    """Same chart with arrows pointing at 50, 55, 60, 65, 70 heads."""
    apply_story_style()
    n = 100
    ks, pmf = _binom_pmf(n)
    tails, _ = _symmetric_surprise_zone(n, pmf, 0.05)
    colors = [PALETTE["contrast"] if k in tails else PALETTE["focus"] for k in ks]

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(ks, pmf, color=colors, width=0.85)
    ax.set_xlabel("number of heads in 100 tosses")
    ax.set_ylabel("how often this would happen with a fair coin")
    ax.set_xlim(0, 100)
    ymax = max(pmf) * 1.32
    ax.set_ylim(0, ymax)

    observations = [50, 55, 60, 65, 70]
    for obs in observations:
        height = pmf[obs]
        ax.annotate(
            f"{obs}",
            xy=(obs, height),
            xytext=(obs, ymax * 0.93),
            fontsize=11, ha="center", color=PALETTE["ink"],
            arrowprops=dict(
                arrowstyle="->",
                color=PALETTE["ink"], lw=1.0,
            ),
        )
    out = IMG_DIR / "my_observations_on_the_chart.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_threshold_knob():
    """Three panels showing the surprise zone at 10%, 5%, 1%."""
    apply_story_style()
    n = 100
    ks, pmf = _binom_pmf(n)
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 3.6), sharey=True)
    thresholds = [0.10, 0.05, 0.01]
    for ax, thr in zip(axes, thresholds):
        tails, _ = _symmetric_surprise_zone(n, pmf, thr)
        colors = [PALETTE["contrast"] if k in tails else PALETTE["focus"] for k in ks]
        ax.bar(ks, pmf, color=colors, width=0.85)
        ax.set_xlim(0, 100)
        ax.set_xlabel("number of heads")
        ax.set_title(f"surprise = {int(thr * 100)}%")
        if ax is axes[0]:
            ax.set_ylabel("how often (fair coin)")
    out = IMG_DIR / "threshold_knob.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_belief_after_60():
    """Posterior on p after 60 heads in 100, with the prior shown faintly."""
    apply_story_style()
    ps = np.linspace(0.001, 0.999, 1000)
    # Flat prior Beta(1,1)
    prior = stats.beta.pdf(ps, 1, 1)
    # After 60/100, posterior Beta(61, 41)
    posterior = stats.beta.pdf(ps, 61, 41)

    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(ps, prior, color=PALETTE["muted"], linewidth=1.4, alpha=0.7, label="what I believed before tossing")
    ax.fill_between(ps, 0, posterior, color=PALETTE["focus"], alpha=0.35)
    ax.plot(ps, posterior, color=PALETTE["focus"], linewidth=2.0, label="what I believe after seeing 60 heads in 100")
    ax.axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1.0)
    # 95% credible interval shaded a bit darker
    lo, hi = stats.beta.ppf(0.025, 61, 41), stats.beta.ppf(0.975, 61, 41)
    ax.axvline(lo, color=PALETTE["ink"], linestyle=":", linewidth=0.8)
    ax.axvline(hi, color=PALETTE["ink"], linestyle=":", linewidth=0.8)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, max(posterior) * 1.08)
    ax.set_xlabel("possible fairness of the coin (0 = always tails, 1 = always heads)")
    ax.set_ylabel("how strongly I believe each value")
    ax.legend(loc="upper left")
    out = IMG_DIR / "belief_after_60.png"
    fig.savefig(out)
    plt.close(fig)
    return out, float(lo), float(hi)


def render_fair_vs_biased_overlap():
    """Two histograms overlaid: 10,000 fair runs and 10,000 biased (0.55) runs.

    The point of this picture is to show how much the two distributions
    overlap, so the reader sees why a single 100-toss experiment from a
    biased coin will almost always still land inside the fair-coin
    surprise zone.
    """
    apply_story_style()
    rng = np.random.default_rng(202)
    n_tosses = 100
    n_people = 10000
    fair_counts = rng.binomial(n_tosses, 0.5, size=n_people)
    biased_counts = rng.binomial(n_tosses, 0.55, size=n_people)
    bins = np.arange(0, n_tosses + 2) - 0.5
    fair_hist, _ = np.histogram(fair_counts, bins=bins)
    biased_hist, _ = np.histogram(biased_counts, bins=bins)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ks = np.arange(0, n_tosses + 1)
    ax.bar(ks, fair_hist, color=PALETTE["contrast"], alpha=0.55, width=0.95, label="fair coin (bias 0.50)")
    ax.bar(ks, biased_hist, color=PALETTE["focus"], alpha=0.55, width=0.95, label="biased coin (bias 0.55)")
    ax.set_xlim(20, 80)
    ax.set_xlabel("number of heads (out of 100 tosses)")
    ax.set_ylabel("how many of the 10,000 runs landed there")
    ax.legend(loc="upper right")
    out = IMG_DIR / "fair_vs_biased_overlap.png"
    fig.savefig(out)
    plt.close(fig)
    return out, int(fair_hist.sum()), int(biased_hist.sum())


def render_hump_narrows_with_n():
    """Same fair-coin distribution at N=50, 100, 500, 5000.

    All centered at fraction 0.5, but the spread shrinks as N grows.
    Normalized to the fraction axis so they are comparable on one chart.
    """
    apply_story_style()
    sizes = [50, 100, 500, 5000]
    colors = [PALETTE["focus"], PALETTE["contrast"], PALETTE["support"], PALETTE["ink"]]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for n, color in zip(sizes, colors):
        ks = np.arange(0, n + 1)
        pmf = stats.binom.pmf(ks, n, 0.5)
        fractions = ks / n
        ax.plot(fractions, pmf * n, color=color, linewidth=1.8, alpha=0.85, label=f"{n} tosses")
    ax.set_xlim(0.2, 0.8)
    ax.set_xlabel("fraction of heads (heads / total tosses)")
    ax.set_ylabel("how often each fraction would happen with a fair coin")
    ax.legend(loc="upper right", title="experiment size")
    out = IMG_DIR / "hump_narrows_with_n.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_how_often_I_get_fooled():
    """Empirical rejection rates across truth and N."""
    apply_story_style()
    truths = [0.50, 0.52, 0.55, 0.60]
    sizes = [50, 200, 1000]
    rng = np.random.default_rng(303)
    rates = np.zeros((len(truths), len(sizes)))
    n_trials = 1000
    for i, p in enumerate(truths):
        for j, n in enumerate(sizes):
            counts = rng.binomial(n, p, size=n_trials)
            # Two-sided exact test against H0: p=0.5 at alpha=0.05
            from scipy.stats import binomtest
            rejects = 0
            for k in counts:
                pval = binomtest(int(k), n, p=0.5, alternative="two-sided").pvalue
                if pval < 0.05:
                    rejects += 1
            rates[i, j] = rejects / n_trials

    fig, ax = plt.subplots(figsize=(10, 4.5))
    width = 0.22
    x = np.arange(len(truths))
    for j, n in enumerate(sizes):
        offset = (j - 1) * width
        ax.bar(x + offset, rates[:, j], width=width,
               color=[PALETTE["focus"], PALETTE["contrast"], PALETTE["support"]][j],
               label=f"{n} tosses")
    ax.set_xticks(x)
    ax.set_xticklabels([f"truly fair\n(p = 0.50)" if p == 0.50 else f"slightly heavy\n(p = {p})" for p in truths])
    ax.set_ylabel("how often the test rings the alarm")
    ax.set_ylim(0, 1.05)
    reference_line(ax, 0.05, label="my surprise threshold (5%)")
    ax.legend(loc="upper left")
    out = IMG_DIR / "how_often_I_get_fooled.png"
    fig.savefig(out)
    plt.close(fig)
    return out, rates


def main():
    ensure_dirs()
    paths = []
    p_raw, raw_counts = render_ten_thousand_people_raw()
    paths.append((p_raw, "derived",
                  f"Story Ch.2: 10000-people raw-count histogram, annotated highlights at 35/50/60/65 heads ({raw_counts[35]}/{raw_counts[50]}/{raw_counts[60]}/{raw_counts[65]})"))
    paths.append((render_what_would_I_see_if_fair(), "derived",
                  "Story Ch.2: same shape with vertical axis as percentages"))
    p, lo_cut, hi_cut, tail_mass = render_surprise_tails()
    paths.append((p, "derived",
                  f"Story Ch.2: same histogram with two-sided 5% tails (cutoffs {lo_cut} and {hi_cut}, tail mass {tail_mass:.4f})"))
    paths.append((render_my_observations_on_the_chart(), "derived",
                  "Story Ch.2: histogram with observation pointers at 50, 55, 60, 65, 70"))
    paths.append((render_threshold_knob(), "derived",
                  "Story Ch.2: same histogram across 10%/5%/1% surprise thresholds"))
    p_belief, ci_lo, ci_hi = render_belief_after_60()
    paths.append((p_belief, "derived",
                  f"Story Ch.2: posterior on p after 60/100, Beta(61,41), 95% CI [{ci_lo:.3f}, {ci_hi:.3f}]"))
    p_overlap, _, _ = render_fair_vs_biased_overlap()
    paths.append((p_overlap, 202,
                  "Story Ch.2: fair vs biased(0.55) coin distributions overlaid, 10000 runs each"))
    paths.append((render_hump_narrows_with_n(), "derived",
                  "Story Ch.2: binomial(N, 0.5) hump narrows with N (50, 100, 500, 5000) on fraction axis"))
    p_fooled, rates = render_how_often_I_get_fooled()
    paths.append((p_fooled, 303,
                  f"Story Ch.2: empirical rejection rate, truths {[0.50,0.52,0.55,0.60]} x sizes {[50,200,1000]}, rates {rates.round(3).tolist()}"))

    print(f"Story Ch.2: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
