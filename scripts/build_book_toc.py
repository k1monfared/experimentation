#!/usr/bin/env python3
"""Combine all chapter toc.csv files into a single loglog .log and a self-contained HTML viewer.

The toc.csv files for each chapter map four parallel tracks (Story, Technical, Code, Play) onto
a single concept per row. This script merges all 21 chapter files into:

    book_toc.log    Hierarchical plain text. Structure:
                    Chapter > Big topic > Small topic > [story/tech/code/play]
                    SKIP cells are omitted.

    book_toc.html   Single-file viewer. Folded by default at every level. File references
                    (story.md, chapter.md, images/*, story/*.png, play/*.py) become links.
                    Free-text search, no external dependencies.

Run from repo root:
    python scripts/build_book_toc.py
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = REPO / "chapters"
LOG_OUT = REPO / "book_toc.log"
HTML_OUT = REPO / "book_toc.html"

LOOP_PATTERN = re.compile(r"\bLoop\s+([A-Z](?:\.\d+)?)", re.IGNORECASE)


def chapter_label(dir_name: str) -> str:
    """01-the-coin -> Chapter 01 the coin. A1-mcmc-diagnostics -> Appendix A1 mcmc diagnostics."""
    prefix, _, rest = dir_name.partition("-")
    title = rest.replace("-", " ")
    if prefix.startswith("A"):
        return f"Appendix {prefix}: {title}"
    return f"Chapter {prefix}: {title}"


def is_skip(cell: str) -> bool:
    """A cell that should be omitted from the loglog output."""
    if not cell:
        return True
    c = cell.strip()
    if not c:
        return True
    low = c.lower()
    if low.startswith("skip:") or low.startswith("skip ") or low == "skip":
        return True
    if low.startswith("not applicable") or low.startswith("n/a"):
        return True
    if c in {"-", "."}:
        return True
    return False


def classify_big_topic(technical_cell: str, prev: str | None) -> str:
    """Map a row to its 'big topic'. Heuristic: detect Loop X in the Technical cell.
    Otherwise fall back to prev, or to Framing/Hand-off based on keywords."""
    if not is_skip(technical_cell):
        m = LOOP_PATTERN.search(technical_cell)
        if m:
            return f"Loop {m.group(1).upper()}"
        low = technical_cell.lower()
        if "framing" in low or "carried" in low or "carry-over" in low:
            return "Framing"
        if "hand-off" in low or "handoff" in low or "big question" in low:
            return "Hand-off"
        if "aside" in low:
            return "Aside"
        if "two-lens" in low or "two lens" in low:
            return prev or "Two-lens commentary"
    return prev or "Framing"


def normalize(text: str) -> str:
    """Strip newlines, collapse whitespace."""
    if not text:
        return ""
    return " ".join(text.split())


_NUM_TOKEN = re.compile(r"^\d+\)?$")


def repair_row(row: list[str]) -> list[str]:
    """Some cells contain commas that were not properly quoted. The csv reader
    then split them into multiple fields. Heuristics to glue them back:

    1. A field starting with whitespace is the tail of an unquoted comma split.
    2. A bare numeric token (10, 100, 100), etc) is a list continuation.
    3. If still too many fields, force-merge into the Technical column (index 2).
    """
    if len(row) <= 5:
        while len(row) < 5:
            row.append("")
        return row

    out = [row[0]]
    for cell in row[1:]:
        merge = False
        if out and cell:
            if cell.startswith((" ", "\t")):
                merge = True
            elif _NUM_TOKEN.match(cell.strip()):
                merge = True
        if merge:
            out[-1] = out[-1] + "," + cell
        else:
            out.append(cell)

    while len(out) > 5:
        # Last-resort merge: combine into Technical column.
        out[2] = out[2] + ", " + out[3]
        del out[3]
    while len(out) < 5:
        out.append("")
    return out


PATH_PATTERNS = [
    # play/foo.py
    (re.compile(r"\b(play/[\w/]+\.py)\b"), "{chapter}/{match}"),
    # images/story/foo.png and images/foo.png (full path)
    (re.compile(r"\b(images/[\w/]+\.(?:png|jpg|jpeg|svg))\b"), "{chapter}/{match}"),
    # bare story/foo.png (under images/)
    (re.compile(r"(?<![\w/])(story/[\w/]+\.(?:png|jpg|jpeg|svg))\b"), "{chapter}/images/{match}"),
    # story.md / chapter.md / notebook.ipynb at chapter root
    (re.compile(r"\b(story\.md|chapter\.md|notebook\.ipynb|exercises\.md)\b"), "{chapter}/{match}"),
]


def linkify_paths(text: str, chapter_dir: str) -> str:
    """Convert file path references in cell content to markdown-style [text](url) links.
    The viewer's custom linkify will turn these into <a> tags."""
    if not text:
        return text
    chapter_rel = f"chapters/{chapter_dir}"
    for pattern, tmpl in PATH_PATTERNS:
        def repl(m, t=tmpl):
            match = m.group(1)
            url = t.format(chapter=chapter_rel, match=match)
            return f"[{match}]({url})"
        text = pattern.sub(repl, text)
    return text


def build_log_lines() -> list[str]:
    chapters = sorted(p for p in CHAPTERS_DIR.iterdir() if p.is_dir())
    lines: list[str] = []

    for chap in chapters:
        toc = chap / "toc.csv"
        if not toc.exists():
            continue

        lines.append(chapter_label(chap.name))
        current_big = None

        with open(toc, newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for raw in reader:
                row = repair_row(raw)
                topic = normalize(row[0]).strip()
                if not topic:
                    continue

                story = normalize(row[1])
                tech = normalize(row[2])
                code = normalize(row[3])
                play = normalize(row[4])

                big = classify_big_topic(tech, current_big)
                if big != current_big:
                    lines.append(f"    {big}")
                    current_big = big

                lines.append(f"        {topic}")

                if not is_skip(story):
                    lines.append(f"            - story: {linkify_paths(story, chap.name)}")
                if not is_skip(tech):
                    lines.append(f"            - technical: {linkify_paths(tech, chap.name)}")
                if not is_skip(code):
                    lines.append(f"            - code: {linkify_paths(code, chap.name)}")
                if not is_skip(play):
                    lines.append(f"            - play: {linkify_paths(play, chap.name)}")

    return lines


CSS = r"""
:root {
  --bg: #1a1a1a;
  --bg2: #252525;
  --bg3: #303030;
  --bd: #3a3a3a;
  --txt: #e0e0e0;
  --txt2: #888;
  --acc: #6cb6ff;
  --green: #4caf50;
  --ora: #ff9800;
  --red: #f44336;
}
@media (prefers-color-scheme: light) {
  :root {
    --bg: #fafafa;
    --bg2: #f0f0f0;
    --bg3: #e5e5e5;
    --bd: #d0d0d0;
    --txt: #1a1a1a;
    --txt2: #666;
    --acc: #0066cc;
  }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--bd); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--txt2); }
* { scrollbar-width: thin; scrollbar-color: var(--bd) transparent; }
body {
  background: var(--bg); color: var(--txt);
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 15px; line-height: 1.5;
}

#hdr {
  position: sticky; top: 0; z-index: 100;
  background: var(--bg); border-bottom: 1px solid var(--bd);
  padding: 10px 14px 8px;
}
#hdr h1 { font-size: 1.25rem; color: var(--acc); margin-bottom: 8px; letter-spacing: .5px; }
.search-row { display: flex; gap: 8px; align-items: center; }
#search {
  flex: 1; padding: 7px 12px;
  border-radius: 8px; border: 1px solid var(--bd);
  background: var(--bg2); color: var(--txt); font-size: 14px;
}
#search:focus { outline: none; border-color: var(--acc); }
#search-count { color: var(--txt2); font-size: 12px; white-space: nowrap; }
#stats { padding: 5px 14px; color: var(--txt2); font-size: 12px; border-bottom: 1px solid var(--bd); }

.sec { border-bottom: 1px solid var(--bd); }
.sec-hdr {
  display: flex; align-items: center;
  padding: 9px 14px; cursor: pointer; background: var(--bg2); user-select: none;
}
.sec-hdr:hover { background: var(--bg3); }
.sec-title { font-weight: 600; font-size: .92rem; }
.sec-meta { display: flex; align-items: center; gap: 8px; color: var(--txt2); font-size: 12px; margin-left: auto; }
.arr { color: var(--txt2); font-size: 11px; transition: transform .2s; flex-shrink: 0; width: 12px; text-align: center; margin-right: 6px; }
.sec.open > .sec-hdr .arr { transform: rotate(90deg); }
.sec-body { display: none; }
.sec.open > .sec-body { display: block; }

.sec[data-depth="0"] > .sec-hdr { background: var(--bg2); }
.sec[data-depth="0"] > .sec-hdr .sec-title { color: var(--acc); font-size: 1rem; }
.sec[data-depth="1"] > .sec-hdr { padding-left: 28px; background: var(--bg); }
.sec[data-depth="1"] > .sec-hdr .sec-title { color: var(--txt); font-weight: 500; }
.sec[data-depth="2"] > .sec-hdr { padding-left: 46px; }

.item { border-bottom: 1px solid var(--bd); }
.item-hdr {
  display: flex; align-items: flex-start; gap: 9px;
  padding: 8px 14px 8px 64px; cursor: pointer;
}
.item-hdr:hover { background: var(--bg2); }
.item-info { flex: 1; min-width: 0; }
.item-name { font-weight: 500; font-size: .92rem; }
.item-detail { display: none; padding: 6px 14px 12px 84px; background: var(--bg2); border-top: 1px solid var(--bd); }
.item.open .item-detail { display: block; }
.item.open .item-hdr { background: var(--bg2); }

.dg { display: grid; grid-template-columns: 90px 1fr; gap: 6px 14px; padding: 4px 0; }
.dk { color: var(--txt2); font-size: 12px; text-transform: uppercase; letter-spacing: .5px; padding-top: 2px; }
.dv { font-size: 14px; line-height: 1.55; }
.dv a { color: var(--acc); text-decoration: none; word-break: break-word; }
.dv a:hover { text-decoration: underline; }

.center { text-align: center; padding: 30px; color: var(--txt2); }
.err { color: var(--red); }

.kbd { font-family: ui-monospace, monospace; font-size: 12px; padding: 1px 5px; border-radius: 3px; background: var(--bg3); border: 1px solid var(--bd); color: var(--txt2); }
.foot { padding: 14px; color: var(--txt2); font-size: 11px; text-align: center; }
"""


JS = r"""
(function() {

function buildTree(text) {
  const lines = text.split('\n');
  const root = { raw: '', indent: -1, children: [], lineIdx: -1 };
  const stack = [root];
  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    if (raw.trim() === '') continue;
    const indent = raw.search(/\S/);
    const content = raw.trim();
    while (stack.length > 1 && stack[stack.length - 1].indent >= indent) stack.pop();
    const node = { raw: content, indent, children: [], lineIdx: i };
    stack[stack.length - 1].children.push(node);
    stack.push(node);
  }
  return root.children;
}

function isPropertyLine(raw) {
  return /^-?\s*\w[\w\s/&'()\-]*?:\s/.test(raw);
}

function classifyNode(node, depth) {
  const raw = node.raw;
  const name = raw.replace(/^-\s*/, '').replace(/:$/, '').trim();
  if (!name && node.children.length === 0) return null;

  if (node.children.length === 0) {
    return { type: 'item', name, depth, properties: {}, childTexts: [] };
  }

  const allProp = node.children.every(c => isPropertyLine(c.raw) || (c.children.length === 0));
  const hasPropChild = node.children.some(c => isPropertyLine(c.raw));

  if (allProp && hasPropChild) {
    const item = { type: 'item', name, depth, properties: {}, childTexts: [] };
    for (const child of node.children) {
      const m = child.raw.match(/^-?\s*(\w[\w\s/&'()\-]*?):\s+(.+)$/);
      if (m) {
        item.properties[m[1].trim().toLowerCase()] = m[2].trim();
      } else {
        const t = child.raw.replace(/^-\s*/, '').trim();
        if (t) item.childTexts.push(t);
      }
    }
    return item;
  }

  const children = [];
  for (const c of node.children) {
    const cls = classifyNode(c, depth + 1);
    if (cls) children.push(cls);
  }
  return { type: 'section', name, depth, children };
}

function classifyTree(rawNodes) {
  const result = [];
  for (const n of rawNodes) {
    const c = classifyNode(n, 0);
    if (c) result.push(c);
  }
  return result;
}

function escHtml(s) {
  if (s === undefined || s === null) return '';
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function linkify(text) {
  if (!text) return '';
  // First http(s) URLs
  let out = text.replace(/(https?:\/\/[^\s<>"']+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
  // Then markdown [text](url) — URL is taken verbatim (already a relative path)
  out = out.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m, t, u) => `<a href="${u}" target="_blank" rel="noopener">${t}</a>`);
  return out;
}

function countDescendantItems(node) {
  let c = 0;
  for (const child of (node.children || [])) {
    if (child.type === 'item') c++;
    c += countDescendantItems(child);
  }
  return c;
}

function renderNodes(container, nodes) {
  for (const node of nodes) {
    if (node.type === 'section') renderSection(container, node);
    else renderItem(container, node);
  }
}

function renderSection(container, node) {
  const sec = document.createElement('div');
  sec.className = 'sec';
  sec.dataset.depth = node.depth || 0;
  const count = countDescendantItems(node);
  sec.innerHTML = `
    <div class="sec-hdr">
      <span class="arr">▶</span>
      <span class="sec-title">${escHtml(node.name)}</span>
      <span class="sec-meta"><span>${count || ''}</span></span>
    </div>
    <div class="sec-body"></div>`;
  sec.querySelector('.sec-hdr').addEventListener('click', () => sec.classList.toggle('open'));
  const body = sec.querySelector('.sec-body');
  if (node.children && node.children.length > 0) renderNodes(body, node.children);
  // NOTE: no auto-open. Everything starts folded.
  container.appendChild(sec);
}

function renderItem(container, node) {
  const item = document.createElement('div');
  item.className = 'item';
  item.dataset.depth = node.depth || 0;
  item.dataset.name = (node.name || '').toLowerCase();
  const props = node.properties || {};
  const hasDetail = Object.keys(props).length > 0 || (node.childTexts && node.childTexts.length > 0);
  item.innerHTML = `
    <div class="item-hdr">
      <div class="item-info">
        <div class="item-name">${linkify(escHtml(node.name))}</div>
      </div>
    </div>`;
  if (hasDetail) {
    const detail = document.createElement('div');
    detail.className = 'item-detail';
    const keys = Object.keys(props);
    if (keys.length > 0) {
      const grid = document.createElement('div');
      grid.className = 'dg';
      const order = ['story', 'technical', 'code', 'play'];
      const sortedKeys = keys.sort((a, b) => {
        const ai = order.indexOf(a), bi = order.indexOf(b);
        return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
      });
      for (const k of sortedKeys) {
        const v = props[k];
        grid.innerHTML += `<span class="dk">${escHtml(k)}</span><span class="dv">${linkify(escHtml(v))}</span>`;
      }
      detail.appendChild(grid);
    }
    for (const t of (node.childTexts || [])) {
      const line = document.createElement('div');
      line.className = 'dv';
      line.innerHTML = linkify(escHtml(t));
      detail.appendChild(line);
    }
    item.appendChild(detail);
    item.querySelector('.item-hdr').addEventListener('click', () => item.classList.toggle('open'));
  }
  container.appendChild(item);
}

function filterTree(query) {
  const q = query.trim().toLowerCase();
  const items = document.querySelectorAll('.item');
  const sections = document.querySelectorAll('.sec');
  if (!q) {
    items.forEach(el => { el.style.display = ''; el.classList.remove('open'); });
    sections.forEach(el => { el.style.display = ''; el.classList.remove('open'); });
    document.getElementById('search-count').textContent = '';
    return;
  }
  let visible = 0;
  items.forEach(el => {
    const text = el.textContent.toLowerCase();
    if (text.includes(q)) {
      el.style.display = '';
      el.classList.add('open');
      visible++;
    } else {
      el.style.display = 'none';
      el.classList.remove('open');
    }
  });
  const secArr = Array.from(sections).reverse();
  for (const sec of secArr) {
    const visibleChild = sec.querySelector('.item:not([style*="display: none"]), .sec:not([style*="display: none"])');
    const titleMatch = sec.querySelector('.sec-title').textContent.toLowerCase().includes(q);
    if (visibleChild || titleMatch) {
      sec.style.display = '';
      sec.classList.add('open');
      if (titleMatch && !visibleChild) {
        sec.querySelectorAll('.item').forEach(i => { i.style.display = ''; visible++; });
        sec.querySelectorAll('.sec').forEach(s => { s.style.display = ''; s.classList.add('open'); });
      }
    } else {
      sec.style.display = 'none';
      sec.classList.remove('open');
    }
  }
  document.getElementById('search-count').textContent = `${visible} match${visible !== 1 ? 'es' : ''}`;
}

function main() {
  const dataEl = document.getElementById('loglog-data');
  const text = (dataEl.textContent || '').replace(/^\n+/, '');
  const tree = buildTree(text);
  const nodes = classifyTree(tree);

  const content = document.getElementById('content');
  content.innerHTML = '';
  renderNodes(content, nodes);

  let totalItems = 0;
  function count(ns) { for (const n of ns) { if (n.type === 'item') totalItems++; if (n.children) count(n.children); } }
  count(nodes);
  document.getElementById('stats').textContent = `${totalItems} concepts across ${nodes.length} chapters`;

  document.getElementById('search').addEventListener('input', e => filterTree(e.target.value));
}

document.addEventListener('DOMContentLoaded', main);

})();
"""


def html_template(log_text: str) -> str:
    # Inline the loglog text inside <script type="text/plain"> — needs to escape </script>
    safe_log = log_text.replace("</script>", "<\\/script>")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Book TOC: experimentation</title>
<style>{CSS}</style>
</head>
<body>
<div id="hdr">
  <h1>Book TOC: experimentation</h1>
  <div class="search-row">
    <input id="search" type="text" placeholder="Search by topic, content, or file path..." autocomplete="off" />
    <span id="search-count"></span>
  </div>
</div>
<div id="stats">Loading...</div>
<div id="content"><div class="center">Loading...</div></div>
<div class="foot">Click a chapter to expand. Click a small topic to see its story / technical / code / play content. File references are clickable.</div>
<script type="text/plain" id="loglog-data">
{safe_log}</script>
<script>{JS}</script>
</body>
</html>
"""


def main() -> None:
    lines = build_log_lines()
    log_text = "\n".join(lines) + "\n"

    LOG_OUT.write_text(log_text)
    print(f"Wrote {LOG_OUT.relative_to(REPO)} ({len(lines)} lines)")

    HTML_OUT.write_text(html_template(log_text))
    print(f"Wrote {HTML_OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
