#!/usr/bin/env python3
"""Claude Code UserPromptSubmit hook: surface past notes/threads related to the prompt.

Reads QMD's full-text index (read-only, ~30ms). FTS5 pulls ~80 candidates matching ANY of
the prompt's distinctive words, then they are re-ranked in Python: how many *distinct*
prompt words a doc covers (rare words count more), recency, and a boost for decision
sources (Claude memory, docs/details). Plain bm25 let huge Coordinator threads, which
mention everything, win on sheer volume (2026-10-29: Deepgram vs Speechify was missed).
Prints up to 4 one-line pointers; Claude Code adds stdout to the prompt's context and
Claude opens a pointer with the qmd MCP `get` tool only if it's useful.
Fails silently: a broken hook must never block a prompt.
"""
import datetime
import json
import math
import os
import re
import sqlite3
import sys

INDEX = os.path.expanduser("~/.cache/qmd/index.sqlite")
MAX_HITS = 4
# Decision sources outrank chatter; coordinators mention everything, so they are damped.
COLLECTION_BOOST = {"memory": 1.6, "details": 1.4, "vault": 1.1, "claude-threads": 1.0,
                    "gemini-threads": 0.7, "antigravity-threads": 0.6}
NOISY_TITLE = re.compile(r"coordinator", re.I)
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
            "SELECT f.rowid, f.filepath, f.title, d.collection, d.modified_at FROM documents_fts f "
            "JOIN documents d ON d.id = f.rowid AND d.active = 1 "
            "WHERE documents_fts MATCH ? ORDER BY bm25(documents_fts, 1.0, 8.0, 1.0) LIMIT 250",
            (match,),
        ).fetchall()
        if not rows:
            return
        ids = ",".join(str(r[0]) for r in rows)
        # Which prompt words each candidate contains, and how common each word is overall.
        hits = {r[0]: set() for r in rows}
        df = {}
        for w in words:
            q = f'"{w}"'
            df[w] = db.execute("SELECT count(*) FROM documents_fts WHERE documents_fts MATCH ?", (q,)).fetchone()[0]
            for (rid,) in db.execute(
                f"SELECT rowid FROM documents_fts WHERE documents_fts MATCH ? AND rowid IN ({ids})", (q,)
            ):
                hits[rid].add(w)
        total = db.execute("SELECT count(*) FROM documents WHERE active = 1").fetchone()[0] or 1
    except Exception:
        return
    now = datetime.datetime.now(datetime.timezone.utc)
    scored = []
    for rank, (rid, path, title, coll, mtime) in enumerate(rows):
        # Squared IDF: a rare name the prompt mentions (Deepgram, df 21) beats many common words.
        idf = sum(math.log(1 + total / (1 + df[w])) ** 2 for w in hits[rid])
        try:
            age = (now - datetime.datetime.fromisoformat(mtime.replace("Z", "+00:00"))).days
        except Exception:
            age = 60
        score = idf * COLLECTION_BOOST.get(coll, 1.0) * (1 + 1.0 / (1 + age / 7))
        score *= 1 - rank / 1000  # keep a little of bm25's opinion
        if path.endswith("/MEMORY.md"):
            continue  # the memory index lists everything
        if NOISY_TITLE.search(title or ""):
            score *= 0.5
        scored.append((score, path, title))
    scored.sort(reverse=True)
    rows = [(p, t) for _, p, t in scored]
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
        print("Possibly related past notes/threads (QMD keyword match, decisions + recent first; open with the qmd `get` tool only if relevant, ignore otherwise):")
        print("\n".join(lines))


if __name__ == "__main__":
    main()
