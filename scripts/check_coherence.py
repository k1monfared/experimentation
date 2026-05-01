"""Cross-chapter coherence check.

Walks every chapter.log and extracts:
- the "Big question" (the single one-sentence question that ends the chapter)
- the "Carried from" line at the top of the next chapter

Prints them paired. Drift between them indicates a chapter-to-chapter handoff
that needs tightening. Exits 0 always; this is a diagnostic, not a guard.
"""

from __future__ import annotations

import re
from pathlib import Path

CHAPTERS_DIR = Path(__file__).resolve().parent.parent / "chapters"


def extract_big_question(text: str) -> str:
    """Find a 'Big question' bullet near the end of a chapter.log."""
    # Look for 'Big question' followed by content
    matches = re.findall(r"Big question[:\-\s]+(.+?)(?:\n|$)", text, flags=re.IGNORECASE)
    if matches:
        return matches[-1].strip()
    return ""


def extract_carried_from(text: str) -> str:
    """Find the 'Carried from' bullet near the top of a chapter.log."""
    # Find first occurrence of "Carried from"
    m = re.search(r"Carried from[^\n]*\n((?:\s+- .+\n)+)", text)
    if m:
        # Concatenate the bullet body lines
        body = m.group(1)
        # Strip leading bullet markers
        cleaned = " ".join(line.strip(" -\t") for line in body.splitlines() if line.strip())
        return cleaned[:300]
    return ""


def main() -> int:
    chapter_dirs = sorted(d for d in CHAPTERS_DIR.iterdir() if d.is_dir())
    big_qs = {}
    carried = {}
    for d in chapter_dirs:
        log_path = d / "chapter.log"
        if not log_path.exists():
            continue
        text = log_path.read_text()
        big_qs[d.name] = extract_big_question(text)
        carried[d.name] = extract_carried_from(text)

    print(f"Loaded {len(chapter_dirs)} chapters\n")

    for prev, nxt in zip(chapter_dirs[:-1], chapter_dirs[1:]):
        bq = big_qs.get(prev.name, "")
        cf = carried.get(nxt.name, "")
        print(f"=== {prev.name} -> {nxt.name} ===")
        print(f"  Big question : {bq}")
        print(f"  Carried from : {cf}")
        if not bq:
            print("  ! WARNING: previous chapter has no detectable Big question")
        if not cf:
            print("  ! WARNING: next chapter has no detectable Carried-from")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
