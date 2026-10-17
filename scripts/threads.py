#!/usr/bin/env python3
"""Read-only lookup of Matt's old AI threads (Gemini, Antigravity, Hermes, etc.).

Source: Hermes DB ~/.hermes/state.db (opened read-only; never written).

  threads.py search "<words>" [--source gemini-archive] [--limit 15]
  threads.py recent [--source gemini-archive] [--limit 20]
  threads.py show <session_id> [--max-chars 60000]
"""
import argparse
import datetime
import os
import sqlite3
import sys

DB = os.path.expanduser("~/.hermes/state.db")


def connect():
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)


def fmt_ts(ts):
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else "?"


def fts_query(words):
    # Quote each term so punctuation can't break FTS syntax; all terms must match.
    return " ".join('"' + w.replace('"', '""') + '"' for w in words.split())


def search(args):
    db = connect()
    where_src = "AND s.source = ?" if args.source else ""
    params = [fts_query(args.query)] + ([args.source] if args.source else []) + [args.limit]
    # snippet() can't be used under GROUP BY, so group in Python.
    hits = db.execute(
        f"""
        SELECT s.id, s.source, s.started_at, COALESCE(s.title, ''),
               snippet(messages_fts, 0, '[', ']', '…', 12)
        FROM messages_fts
        JOIN messages m ON m.id = messages_fts.rowid
        JOIN sessions s ON s.id = m.session_id
        WHERE messages_fts MATCH ? {where_src}
        LIMIT 2000
        """,
        params[:-1],
    ).fetchall()
    by_session = {}
    for sid, src, ts, title, snip in hits:
        entry = by_session.setdefault(sid, [sid, src, ts, title, 0, snip])
        entry[4] += 1
    rows = sorted(by_session.values(), key=lambda r: (-r[4], -(r[2] or 0)))[: args.limit]
    if not rows:
        print("No matches. Try fewer or different words.")
    for sid, src, ts, title, hits, snip in rows:
        print(f"{sid}  {fmt_ts(ts)}  {src:<16} hits={hits:<3} {title}")
        print(f"    {' '.join(snip.split())}")


def recent(args):
    db = connect()
    where = "WHERE source = ?" if args.source else ""
    params = ([args.source] if args.source else []) + [args.limit]
    for sid, src, ts, title, n in db.execute(
        f"SELECT id, source, started_at, COALESCE(title,''), message_count FROM sessions "
        f"{where} ORDER BY COALESCE(last_activity_at, started_at) DESC LIMIT ?",
        params,
    ):
        print(f"{sid}  {fmt_ts(ts)}  {src:<16} msgs={n:<4} {title}")


def show(args):
    db = connect()
    s = db.execute(
        "SELECT source, started_at, COALESCE(title,'') FROM sessions WHERE id = ?", (args.session_id,)
    ).fetchone()
    if not s:
        sys.exit(f"No session {args.session_id}")
    out = [f"# {s[2]}\nsource={s[0]} started={fmt_ts(s[1])} id={args.session_id}\n"]
    for role, content in db.execute(
        "SELECT role, content FROM messages WHERE session_id = ? AND role IN ('user','assistant') "
        "AND content IS NOT NULL AND content != '' ORDER BY timestamp, id",
        (args.session_id,),
    ):
        out.append(f"\n## {role}\n{content.strip()}\n")
    text = "".join(out)
    if len(text) > args.max_chars:
        cut = len(text) - args.max_chars
        text = f"[…{cut} earlier chars omitted; rerun with larger --max-chars]\n" + text[-args.max_chars:]
    print(text)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("search"); a.add_argument("query"); a.add_argument("--source"); a.add_argument("--limit", type=int, default=15)
    a.set_defaults(fn=search)
    b = sub.add_parser("recent"); b.add_argument("--source"); b.add_argument("--limit", type=int, default=20)
    b.set_defaults(fn=recent)
    c = sub.add_parser("show"); c.add_argument("session_id"); c.add_argument("--max-chars", type=int, default=60000)
    c.set_defaults(fn=show)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
