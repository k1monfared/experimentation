"""Render every chapter's ``chapter.log`` to ``chapter.md`` using the loglog CLI.

Falls back to a no-op if the loglog CLI is not on PATH or at the expected
sibling-repo location.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SIBLING_LOGLOG = Path("/home/k1/public/loglog/loglog_cli.py")


def find_loglog_cmd() -> list[str] | None:
    """Locate a working loglog CLI invocation, or None if unavailable."""
    if SIBLING_LOGLOG.is_file():
        return [sys.executable, str(SIBLING_LOGLOG)]
    if shutil.which("loglog"):
        return ["loglog"]
    return None


def render_one(cmd: list[str], log_path: Path) -> None:
    """Render a single .log file to .md alongside it.

    The loglog CLI writes ``<basename>.md`` into ``--output-dir``, so we point
    it at the file's parent directory and pass ``--overwrite`` so re-runs are
    idempotent.
    """
    subprocess.run(
        [*cmd, "convert", str(log_path), "--to", "md", "--output-dir", str(log_path.parent), "--overwrite"],
        check=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapter", help="Render only this chapter (e.g. 01-the-coin)")
    args = parser.parse_args(argv)

    cmd = find_loglog_cmd()
    if cmd is None:
        print("loglog CLI not found. Install or place at /home/k1/public/loglog/loglog_cli.py.", file=sys.stderr)
        return 1

    chapters = REPO_ROOT / "chapters"
    log_paths = sorted(chapters.glob("*/chapter.log"))
    if args.chapter:
        log_paths = [p for p in log_paths if p.parent.name == args.chapter]
        if not log_paths:
            print(f"No chapter named {args.chapter!r} with a chapter.log", file=sys.stderr)
            return 1

    # Also render the top-level README.log if present.
    readme_log = REPO_ROOT / "README.log"
    if readme_log.exists() and not args.chapter:
        log_paths = [readme_log, *log_paths]

    if not log_paths:
        print("No .log files to render.")
        return 0

    print(f"Rendering {len(log_paths)} file(s):")
    for log_path in log_paths:
        rel = log_path.relative_to(REPO_ROOT)
        print(f"  -> {rel}")
        render_one(cmd, log_path)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
