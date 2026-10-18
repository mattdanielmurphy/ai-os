#!/usr/bin/env python3
"""Claude Code UserPromptSubmit hook: surface past notes/threads related to the prompt.

Reads QMD's full-text index (read-only, ~20ms) and ranks documents matching ANY of the
prompt's distinctive words, titles weighted highest. `qmd search` needs every word to
match, which finds nothing for a normal sentence, so the hook queries the index directly.
Prints up to 4 one-line pointers; Claude Code adds stdout to the prompt's context and
Claude opens a pointer with the qmd MCP `get` tool only if it's useful.
Fails silently: a broken hook must never block a prompt.
"""
import json
import os
import re
import sqlite3
import sys

INDEX = os.path.expanduser("~/.cache/qmd/index.sqlite")
MAX_HITS = 4
STOP = set("""
about after again also always another anything because been before being could does doing done
don't each even every from going gonna have here into just know like make maybe more most much
need never only other over really right should some something still such sure take than that
thats their them then there these they thing things think this those through want wanna what
when where which while will with would your yeah okay basically actually kind sort pretty
please thanks thank can't won't it's i'm you're let's we're
""".split())


def keywords(prompt, limit=20):
    seen, out = set(), []
    for w in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{3,}", prompt.lower()):
        if w in STOP or w in seen:
            continue
        seen.add(w)
        out.append(w)
    return out[:limit]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    prompt = (data.get("prompt") or "").strip()
    if len(prompt) < 25 or prompt.startswith("/"):
        return
    words = keywords(prompt)
    if len(words) < 2:
        return
    match = " OR ".join(f'"{w}"' for w in words)
    try:
        db = sqlite3.connect(f"file:{INDEX}?mode=ro", uri=True, timeout=1)
        rows = db.execute(
            "SELECT f.filepath, f.title FROM documents_fts f "
            "JOIN documents d ON d.collection || '/' || d.path = f.filepath AND d.active = 1 "
            "WHERE documents_fts MATCH ? ORDER BY bm25(documents_fts, 1.0, 8.0, 1.0) LIMIT 12",
            (match,),
        ).fetchall()
    except Exception:
        return
    own = (data.get("session_id") or "")[:8]
    lines, titles = [], set()
    for path, title in rows:
        title = (title or "").replace("\n", " ")[:70]
        if (own and own in path) or title in titles:
            continue  # this thread's own export, or the same thread from another archive
        titles.add(title)
        lines.append(f"- {title} — qmd://{path}")
        if len(lines) >= MAX_HITS:
            break
    if lines:
        print("Possibly related past notes/threads (QMD keyword match; open with the qmd `get` tool only if relevant, ignore otherwise):")
        print("\n".join(lines))


if __name__ == "__main__":
    main()
