"""Regenerate every chapter's data artifacts from seed.

Walks ``chapters/*/generate.py`` in order and runs each. Each chapter's
``generate.py`` is responsible for writing its own data files and updating its
own row in ``data/manifest.yaml``. This script orchestrates, then normalizes
the manifest (sorts by path, drops entries whose files no longer exist) so the
on-disk order reflects current state rather than accumulation history.
"""

from __future__ import annotations

import argparse
import runpy
import sys
import time
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.yaml"


def find_generators() -> list[Path]:
    chapters = REPO_ROOT / "chapters"
    return sorted(p for p in chapters.glob("*/generate.py") if p.is_file())


def normalize_manifest() -> tuple[int, int]:
    """Sort manifest entries by path, drop entries pointing to missing files.

    Returns ``(kept, dropped)``. The on-disk order after this matches the
    sorted-by-path order, so re-running ``regenerate_all.py`` from a clean
    state is byte-for-byte stable.
    """
    if not MANIFEST_PATH.exists():
        return (0, 0)
    manifest = yaml.safe_load(MANIFEST_PATH.read_text()) or {"artifacts": []}
    artifacts = manifest.get("artifacts", [])
    kept = []
    dropped = 0
    for art in artifacts:
        rel = art.get("path")
        if rel and (REPO_ROOT / rel).exists():
            kept.append(art)
        else:
            dropped += 1
    kept.sort(key=lambda a: a.get("path", ""))
    manifest["artifacts"] = kept
    MANIFEST_PATH.write_text(yaml.safe_dump(manifest, sort_keys=False))
    return (len(kept), dropped)


def run_one(script: Path) -> None:
    chapter = script.parent.name
    start = time.perf_counter()
    print(f"  -> {chapter} ... ", end="", flush=True)
    runpy.run_path(str(script), run_name="__main__")
    print(f"done ({time.perf_counter() - start:.1f}s)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapter", help="Run only this chapter (e.g. 01-the-coin)")
    args = parser.parse_args(argv)

    scripts = find_generators()
    if args.chapter:
        scripts = [s for s in scripts if s.parent.name == args.chapter]
        if not scripts:
            print(f"No chapter named {args.chapter!r} with a generate.py", file=sys.stderr)
            return 1

    if not scripts:
        print("No generate.py scripts found.")
        return 0

    print(f"Regenerating {len(scripts)} chapter(s):")
    for script in scripts:
        run_one(script)
    if not args.chapter:
        kept, dropped = normalize_manifest()
        print(f"Manifest: {kept} entries (sorted by path, {dropped} stale dropped)")
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
