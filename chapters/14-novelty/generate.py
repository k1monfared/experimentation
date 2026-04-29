"""Regenerate Chapter 14 (novelty effects) figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from expkit.io.samples import _sha256_file  # noqa: E402
from expkit.novelty.measure import (  # noqa: E402
    by_calendar_day,
    by_days_since_exposure,
    by_exposure_count,
)
from expkit.plot.style import PALETTE, apply_style  # noqa: E402
from expkit.sim.novelty import novelty_event_log  # noqa: E402

CHAPTER = "14-novelty"
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


def render_three_views(manifest):
    """Same event log, three measurement schemes."""
    apply_style()
    df = novelty_event_log(n_users=2000, days=40, base_rate=0.10, initial_lift=0.06, half_life_days=5.0, seed=140)
    df.to_parquet(DATA_DIR / "novelty_event_log.parquet")
    add_artifact(manifest, path=DATA_DIR / "novelty_event_log.parquet", kind="samples", seed=140, sha256=_sha256_file(DATA_DIR / "novelty_event_log.parquet"), description="Loop A: novelty event log (2,000 users, 40 days)")

    cal = by_calendar_day(df)
    sin = by_days_since_exposure(df)
    cnt = by_exposure_count(df)

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), sharey=True)
    # By calendar day
    axes[0].plot(cal["day"], cal["control"], label="control", color=PALETTE["frequentist"])
    axes[0].plot(cal["day"], cal["treatment"], label="treatment", color=PALETTE["bayesian"])
    axes[0].axhline(0.10, color=PALETTE["muted"], linestyle="--", linewidth=1, label="true base = 0.10")
    axes[0].set_xlabel("calendar day")
    axes[0].set_title("by calendar day")
    axes[0].legend(fontsize=8)
    # By days since first exposure
    axes[1].plot(sin["days_since_first_exposure"], sin["treatment"], color=PALETTE["bayesian"], label="treatment")
    axes[1].axhline(sin["control"].iloc[0], color=PALETTE["frequentist"], linestyle="-", linewidth=1, label="control overall")
    axes[1].set_xlabel("days since first exposure")
    axes[1].set_title("by per-user time since exposure")
    axes[1].legend(fontsize=8)
    # By exposure count
    cnt_filtered = cnt[cnt["exposure_count"] > 0]
    axes[2].plot(cnt_filtered["exposure_count"], cnt_filtered["treatment"], color=PALETTE["bayesian"], label="treatment")
    axes[2].axhline(cnt_filtered["control"].iloc[0], color=PALETTE["frequentist"], linestyle="-", linewidth=1, label="control overall")
    axes[2].set_xlabel("exposure count")
    axes[2].set_title("by exposure count")
    axes[2].legend(fontsize=8)
    fig.suptitle("Loop A: same event log, three measurement schemes, three stories")
    fig.tight_layout()
    out = IMG_DIR / "three_views.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def render_decay_shapes():
    """Compare decay, primacy, U-shape."""
    apply_style()
    days = np.arange(0, 40)
    decay = 0.06 * np.exp(-days / 5)
    primacy = 0.06 * (1 - np.exp(-days / 10))
    u_shape = 0.06 * np.cos(days / 12) ** 2 - 0.02
    fig, ax = plt.subplots()
    ax.plot(days, decay, label="decay (typical novelty)", color=PALETTE["bayesian"])
    ax.plot(days, primacy, label="primacy (slow ramp-up)", color=PALETTE["frequentist"])
    ax.plot(days, u_shape, label="U-shape", color=PALETTE["highlight"])
    ax.axhline(0, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_xlabel("days since exposure")
    ax.set_ylabel("conversion lift")
    ax.set_title("Loop C: not all temporal patterns are decay")
    ax.legend()
    fig.tight_layout()
    out = IMG_DIR / "decay_shapes.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ensure_dirs()
    manifest = load_manifest()
    paths = [
        render_three_views(manifest),
        render_decay_shapes(),
    ]
    for p in paths:
        add_artifact(manifest, path=p, kind="image", seed="derived", sha256=_sha256_file(p), description=f"Chapter 14 figure: {p.name}")
    save_manifest(manifest)
    print(f"Chapter 14: wrote {len(paths)} figures")


if __name__ == "__main__":
    main()
