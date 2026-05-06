"""Regenerate Chapter 3 (How many tosses do I need) story-track figures.

Multiple figures, written to ``images/story/`` and tracked in
``data/manifest.yaml``. Built around showing each chart in non-log
form first, then progressively in log form to motivate the scale
change.
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
from expkit.plot.story import PALETTE, apply_story_style, reference_line  # noqa: E402

CHAPTER = "03-power"
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


def _power_two_sided(p_alt, n, alpha=0.05):
    z = stats.norm.ppf(1 - alpha / 2)
    se_null = np.sqrt(0.5 * 0.5 / n)
    se_alt = np.sqrt(p_alt * (1 - p_alt) / n)
    upper = (0.5 + z * se_null - p_alt) / se_alt
    lower = (0.5 - z * se_null - p_alt) / se_alt
    return float(stats.norm.sf(upper) + stats.norm.cdf(lower))


def render_detection_grows_linear():
    """Same data as detection_grows_with_n but on a linear x-axis.

    The point of showing this first is to let the reader see why the log
    scale is needed: the early values crush against the y-axis.
    """
    apply_story_style()
    ns = np.arange(10, 5001)
    powers = np.array([_power_two_sided(0.55, n) for n in ns])
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(ns, powers, color=PALETTE["focus"], linewidth=2)
    reference_line(ax, 0.8, label="80 percent: a common target")
    ax.set_xlim(0, 5000)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("number of tosses (linear)")
    ax.set_ylabel("how often the rule catches a real bias of 0.55")
    ax.legend()
    out = IMG_DIR / "detection_grows_linear.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_detection_grows_log():
    """Same data on log x-axis. Lets the reader see the small-N region."""
    apply_story_style()
    ns = np.unique(np.round(np.geomspace(10, 10000, 200)).astype(int))
    powers = np.array([_power_two_sided(0.55, n) for n in ns])
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(ns, powers, color=PALETTE["focus"], linewidth=2)
    reference_line(ax, 0.8, label="80 percent: a common target")
    reference_line(ax, 0.05, color=PALETTE["muted"])
    ax.set_xscale("log")
    ax.set_xlim(10, 10000)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("number of tosses (log scale: each step multiplies by 10)")
    ax.set_ylabel("how often the rule catches a real bias of 0.55")
    ax.legend()
    # annotate a few specific points
    for n_anchor, label_pos in [(100, "right"), (780, "left"), (2000, "right")]:
        p = _power_two_sided(0.55, n_anchor)
        ax.scatter([n_anchor], [p], color=PALETTE["ink"], s=30, zorder=5)
        offset = (10, -8) if label_pos == "right" else (-8, -8)
        ha = "left" if label_pos == "right" else "right"
        ax.annotate(f"{n_anchor} tosses\n catches {p * 100:.0f}%",
                    xy=(n_anchor, p), xytext=offset, textcoords="offset points",
                    fontsize=9, color=PALETTE["ink"], ha=ha)
    out = IMG_DIR / "detection_grows_log.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_detection_at_different_biases():
    """Power curves for several biases. Color order: 0.7 most prominent (focus),
    0.51 most washed out (muted)."""
    apply_story_style()
    ns = np.unique(np.round(np.geomspace(10, 100000, 200)).astype(int))
    # Order biases so the obvious one (0.7) gets the most prominent color.
    biases_with_color = [
        (0.70, PALETTE["focus"]),
        (0.60, PALETTE["contrast"]),
        (0.55, PALETTE["support"]),
        (0.52, "#7a9b76"),
        (0.51, PALETTE["muted"]),
    ]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for bias, color in biases_with_color:
        powers = [_power_two_sided(bias, n) for n in ns]
        ax.plot(ns, powers, color=color, linewidth=2, label=f"bias = {bias}")
    reference_line(ax, 0.8, color=PALETTE["muted"])
    ax.set_xscale("log")
    ax.set_xlim(10, 100000)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("number of tosses (log scale)")
    ax.set_ylabel("how often the rule catches the bias")
    ax.legend(loc="lower right")
    out = IMG_DIR / "detection_at_different_biases.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def _required_n(p_alt, target_power=0.8, alpha=0.05, n_max=1_000_000):
    lo, hi = 4, n_max
    if _power_two_sided(p_alt, hi, alpha) < target_power:
        return n_max
    while lo < hi:
        mid = (lo + hi) // 2
        if _power_two_sided(p_alt, mid, alpha) >= target_power:
            hi = mid
        else:
            lo = mid + 1
    return lo


def render_required_n_linear():
    apply_story_style()
    biases = np.linspace(0.501, 0.80, 100)
    n_required = np.array([_required_n(b) for b in biases])
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot((biases - 0.5) * 100, n_required, color=PALETTE["focus"], linewidth=2)
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 25000)
    ax.set_xlabel("size of the bias I want to catch (percentage points above fair)")
    ax.set_ylabel("number of tosses needed for 80 percent detection (linear)")
    out = IMG_DIR / "required_n_linear.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_required_n_log():
    """Required-N vs effect size on log y-axis."""
    apply_story_style()
    biases = np.linspace(0.501, 0.80, 100)
    n_required = np.array([_required_n(b) for b in biases])
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot((biases - 0.5) * 100, n_required, color=PALETTE["focus"], linewidth=2)
    ax.set_yscale("log")
    ax.set_xlim(0, 30)
    ax.set_xlabel("size of the bias I want to catch (percentage points above fair)")
    ax.set_ylabel("number of tosses needed (log scale)")
    landmarks = [0.51, 0.52, 0.55, 0.60, 0.70]
    for b in landmarks:
        n = _required_n(b)
        ax.scatter([(b - 0.5) * 100], [n], color=PALETTE["ink"], s=30, zorder=5)
        ax.annotate(f"  bias {b}: {n:,} tosses", xy=((b - 0.5) * 100, n),
                    xytext=(8, 0), textcoords="offset points",
                    fontsize=9, color=PALETTE["ink"], va="center")
    out = IMG_DIR / "required_n_log.png"
    fig.savefig(out)
    plt.close(fig)
    return out, {b: int(_required_n(b)) for b in landmarks}


def _mde(n, target_power=0.8, alpha=0.05):
    lo, hi = 0.5001, 0.999
    if _power_two_sided(hi, n, alpha) < target_power:
        return float("nan")
    for _ in range(60):
        mid = (lo + hi) / 2
        if _power_two_sided(mid, n, alpha) >= target_power:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2 - 0.5


def render_mde_progression():
    """MDE chart in three forms: linear, x-log, both-log."""
    apply_story_style()
    ns = np.unique(np.round(np.geomspace(20, 1_000_000, 200)).astype(int))
    mdes = np.array([_mde(n) for n in ns])

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.0), sharey=False)

    axes[0].plot(ns, mdes * 100, color=PALETTE["focus"], linewidth=2)
    axes[0].set_xlim(0, 1_000_000)
    axes[0].set_xlabel("number of tosses (linear)")
    axes[0].set_ylabel("smallest catchable bias\n(percentage points above fair)")
    axes[0].set_title("linear axes: most of the chart is empty")

    axes[1].plot(ns, mdes * 100, color=PALETTE["focus"], linewidth=2)
    axes[1].set_xscale("log")
    axes[1].set_xlim(20, 1_000_000)
    axes[1].set_xlabel("number of tosses (log scale)")
    axes[1].set_ylabel("smallest catchable bias\n(percentage points above fair)")
    axes[1].set_title("log on x: now the small-N detail shows")

    axes[2].plot(ns, mdes * 100, color=PALETTE["focus"], linewidth=2)
    axes[2].set_xscale("log")
    axes[2].set_yscale("log")
    axes[2].set_xlim(20, 1_000_000)
    axes[2].set_xlabel("number of tosses (log scale)")
    axes[2].set_ylabel("smallest catchable bias (log scale)")
    axes[2].set_title("log on both: now the curve is a straight line")

    out = IMG_DIR / "mde_progression.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_three_knobs_annotated():
    """Three-panel triptych, annotated, with per-panel y-axis."""
    apply_story_style()
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    ns = np.unique(np.round(np.geomspace(10, 10000, 100)).astype(int))

    # Panel 1: bias=0.55 fixed, three thresholds
    for alpha, color, label in [(0.10, "#7a9b76", "loose (10%)"),
                                (0.05, PALETTE["focus"], "default (5%)"),
                                (0.01, PALETTE["contrast"], "strict (1%)")]:
        powers = [_power_two_sided(0.55, n, alpha) for n in ns]
        axes[0].plot(ns, powers, color=color, linewidth=1.7, label=label)
    reference_line(axes[0], 0.8, color=PALETTE["muted"])
    # Find intersection points of each curve with the 0.8 line
    for alpha, color in [(0.10, "#7a9b76"), (0.05, PALETTE["focus"]), (0.01, PALETTE["contrast"])]:
        # Find n where power crosses 0.8
        for n in ns:
            if _power_two_sided(0.55, n, alpha) >= 0.8:
                axes[0].scatter([n], [0.8], color=color, s=40, zorder=5)
                axes[0].annotate(f"{n}", xy=(n, 0.8), xytext=(0, 6),
                                  textcoords="offset points", fontsize=8,
                                  color=color, ha="center")
                break
    axes[0].set_title("changing the threshold\n(bias fixed at 0.55)")
    axes[0].legend(fontsize=8, loc="lower right")
    axes[0].set_xscale("log")
    axes[0].set_xlim(10, 10000)
    axes[0].set_ylim(0, 1.02)
    axes[0].set_xlabel("number of tosses")
    axes[0].set_ylabel("how often the rule fires")

    # Panel 2: threshold fixed at 5%, three biases
    for bias, color, label in [(0.52, "#7a9b76", "tiny bias (0.52)"),
                               (0.55, PALETTE["focus"], "small bias (0.55)"),
                               (0.65, PALETTE["contrast"], "obvious bias (0.65)")]:
        powers = [_power_two_sided(bias, n) for n in ns]
        axes[1].plot(ns, powers, color=color, linewidth=1.7, label=label)
    reference_line(axes[1], 0.8, color=PALETTE["muted"])
    for bias, color in [(0.52, "#7a9b76"), (0.55, PALETTE["focus"]), (0.65, PALETTE["contrast"])]:
        for n in ns:
            if _power_two_sided(bias, n) >= 0.8:
                axes[1].scatter([n], [0.8], color=color, s=40, zorder=5)
                axes[1].annotate(f"{n}", xy=(n, 0.8), xytext=(0, 6),
                                  textcoords="offset points", fontsize=8,
                                  color=color, ha="center")
                break
    axes[1].set_title("changing the bias\n(threshold fixed at 5%)")
    axes[1].legend(fontsize=8, loc="lower right")
    axes[1].set_xscale("log")
    axes[1].set_xlim(10, 10000)
    axes[1].set_ylim(0, 1.02)
    axes[1].set_xlabel("number of tosses")
    axes[1].set_ylabel("how often the rule fires")

    # Panel 3: detection target varied, required N
    for target, color, label in [(0.5, "#7a9b76", "50% catch rate"),
                                 (0.8, PALETTE["focus"], "80% catch rate"),
                                 (0.95, PALETTE["contrast"], "95% catch rate")]:
        biases = np.linspace(0.51, 0.70, 80)
        ns_req = []
        for b in biases:
            lo, hi = 4, 1_000_000
            if _power_two_sided(b, hi) < target:
                ns_req.append(hi); continue
            while lo < hi:
                mid = (lo + hi) // 2
                if _power_two_sided(b, mid) >= target:
                    hi = mid
                else:
                    lo = mid + 1
            ns_req.append(lo)
        axes[2].plot((biases - 0.5) * 100, ns_req, color=color, linewidth=1.7, label=label)
    axes[2].set_yscale("log")
    axes[2].set_xlim(1, 20)
    axes[2].set_title("changing the target\n(threshold fixed at 5%)")
    axes[2].set_xlabel("bias above fair (percentage points)")
    axes[2].set_ylabel("number of tosses needed (log scale)")
    axes[2].legend(fontsize=8, loc="upper right")

    out = IMG_DIR / "three_knobs.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_replication_distribution():
    """If I run the experiment 10 times at the recommended N, how many catch the bias?"""
    apply_story_style()
    rng = np.random.default_rng(424)
    bias = 0.55
    n = 780  # recommended for 80% at 0.55
    n_groups = 1000  # how many groups of 10 experiments to simulate
    catches_per_group = []
    for _ in range(n_groups):
        catches = 0
        for _ in range(10):
            head_count = rng.binomial(n, bias)
            pval = stats.binomtest(int(head_count), n, p=0.5, alternative="two-sided").pvalue
            if pval < 0.05:
                catches += 1
        catches_per_group.append(catches)
    catches_per_group = np.array(catches_per_group)
    counts = np.bincount(catches_per_group, minlength=11)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(np.arange(11), counts, color=PALETTE["focus"], width=0.85)
    ax.set_xticks(np.arange(11))
    ax.set_xlabel("how many of 10 experiments caught the bias (each at recommended sample size)")
    ax.set_ylabel(f"how many of {n_groups} groups landed at this number")
    out = IMG_DIR / "replication_distribution.png"
    fig.savefig(out)
    plt.close(fig)
    return out, counts.tolist()


def render_freq_vs_bayes_decisions():
    """Across many simulated experiments, when do the two approaches agree?"""
    apply_story_style()
    rng = np.random.default_rng(7)
    biases = [0.50, 0.52, 0.55, 0.60]
    sizes = [50, 200, 1000]
    n_experiments = 1000
    rows = []
    for bias in biases:
        for n in sizes:
            head_counts = rng.binomial(n, bias, size=n_experiments)
            both_say_biased = 0
            only_freq = 0
            only_bayes = 0
            both_say_fair = 0
            for k in head_counts:
                # Frequentist: surprise zone (5%)
                pval = stats.binomtest(int(k), n, p=0.5, alternative="two-sided").pvalue
                freq_says_biased = pval < 0.05
                # Bayesian: 95% credible interval excludes 0.5
                lo = stats.beta.ppf(0.025, 1 + k, 1 + n - k)
                hi = stats.beta.ppf(0.975, 1 + k, 1 + n - k)
                bayes_says_biased = (lo > 0.5) or (hi < 0.5)
                if freq_says_biased and bayes_says_biased:
                    both_say_biased += 1
                elif freq_says_biased:
                    only_freq += 1
                elif bayes_says_biased:
                    only_bayes += 1
                else:
                    both_say_fair += 1
            rows.append({
                "bias": bias, "n": n,
                "both_biased": both_say_biased,
                "only_freq": only_freq,
                "only_bayes": only_bayes,
                "both_fair": both_say_fair,
                "agree": both_say_biased + both_say_fair,
                "disagree": only_freq + only_bayes,
            })

    fig, axes = plt.subplots(1, len(biases), figsize=(15, 4.5), sharey=True)
    for ax, bias in zip(axes, biases):
        these = [r for r in rows if r["bias"] == bias]
        x = np.arange(len(sizes))
        agree_pct = np.array([r["agree"] / n_experiments * 100 for r in these])
        disagree_pct = np.array([r["disagree"] / n_experiments * 100 for r in these])
        ax.bar(x, agree_pct, color=PALETTE["focus"], width=0.75, label="agreed")
        ax.bar(x, disagree_pct, bottom=agree_pct, color=PALETTE["contrast"], width=0.75, label="disagreed")
        ax.set_xticks(x)
        ax.set_xticklabels([str(n) for n in sizes])
        ax.set_xlabel("number of tosses")
        if ax is axes[0]:
            ax.set_ylabel("percent of 1,000 experiments")
            ax.legend(loc="lower right")
        ax.set_ylim(0, 102)
        ax.set_title(f"bias = {bias}")
    out = IMG_DIR / "freq_vs_bayes_decisions.png"
    fig.savefig(out)
    plt.close(fig)
    return out, rows


def main():
    ensure_dirs()
    paths = []
    paths.append((render_detection_grows_linear(), "derived",
                  "Story Ch.3: detection rate vs N, linear x-axis (motivates log)"))
    paths.append((render_detection_grows_log(), "derived",
                  "Story Ch.3: detection rate vs N, log x-axis with annotated landmarks"))
    paths.append((render_detection_at_different_biases(), "derived",
                  "Story Ch.3: power vs N for several biases, color-fixed (0.7 in focus, 0.51 in muted)"))
    paths.append((render_required_n_linear(), "derived",
                  "Story Ch.3: required N vs effect, linear y (motivates log)"))
    p_req, lm_req = render_required_n_log()
    paths.append((p_req, "derived",
                  f"Story Ch.3: required N vs effect, log y, annotated landmarks ({lm_req})"))
    paths.append((render_mde_progression(), "derived",
                  "Story Ch.3: MDE in three panels (linear, x-log, both-log)"))
    paths.append((render_three_knobs_annotated(), "derived",
                  "Story Ch.3: three-knobs triptych, per-panel y-axis, annotated 80% intersections"))
    p_rep, counts = render_replication_distribution()
    paths.append((p_rep, 424,
                  f"Story Ch.3: replication distribution at bias=0.55, n=780, 10 reps x 1000 groups, counts {counts}"))
    p_fb, fb_rows = render_freq_vs_bayes_decisions()
    paths.append((p_fb, 7,
                  f"Story Ch.3: freq-vs-Bayes decision agreement, biases [0.50,0.52,0.55,0.60] x sizes [50,200,1000]"))

    print(f"Story Ch.3: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
