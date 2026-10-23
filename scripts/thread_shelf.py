#!/usr/bin/env python3
"""Turn a thread snapshot into Everything Shelf documents (the live threads overview artifact).

The shelf page (https://claude.ai/artifact/6Ei7CuXHVYeHvsx94yQH4o) reads its threads from its artifact
database. Only Claude can read project threads (hearthbot tools), so a Claude session gathers
a snapshot and this script shapes it into the one document the page reads, `shelf/current`:

  python3 scripts/thread_shelf.py <threads.json> <out.json> [--resolved resolved.json] [--patch changed.json]
  then ArtifactData set collection "shelf", doc_id "current", file_path <out.json>, if_version <current>

threads.json: [{"id", "title", "bucket", "active", "last": {"by", "at", "text"}, "prev", "cat", "resolved"?}]
  open threads; "prev" = cmsg id this thread was handed off from, or null.
One document (not one per chain) so a refresh is a single pinned write. The page also writes
`requests/<thread id>` docs ({action: "resolve" | "reopen"}) that the refreshing session applies and
deletes, and `notes/<oldest thread id of the chain>` docs ({text, by: "matt" | "claude", at}) itself.
"""
import argparse
import datetime
import json
import os
import re

TAG = {"blocked": "wait", "review_ready": "try", "working": "work"}
CONTINUED = re.compile(r",?\s*(continued|cont\.?|part \d+)$", re.I)


def build(threads):
    by_id = {t["id"]: t for t in threads}
    # A "X, continued" title without an explicit prev link points at the open thread titled "X".
    by_title = {t["title"].strip().lower(): t["id"] for t in threads}
    for t in threads:
        if not t.get("prev"):
            base = CONTINUED.sub("", t["title"]).strip().lower()
            if base != t["title"].strip().lower() and by_title.get(base) not in (None, t["id"]):
                t["prev"] = by_title[base]
    successors = {t["prev"] for t in threads if t.get("prev")}
    chains = {}
    for t in threads:
        if t["id"] in successors:
            continue  # an older link of some chain; it shows behind its newest thread
        links, seen, cur = [], set(), t
        while cur and cur["id"] not in seen:
            seen.add(cur["id"])
            links.append({"id": cur["id"], "title": cur.get("title") or "Earlier thread"})
            nxt = cur.get("prev")
            cur = by_id.get(nxt) or ({"id": nxt, "title": "Earlier thread (resolved)"} if nxt else None)
        chains[t["id"]] = {
            "title": t["title"], "cat": t.get("cat") or "ideas", "tag": TAG.get(t.get("bucket")),
            "active": t.get("active"), "last": t.get("last"), "threads": links, "icon": t.get("icon"),
        }
    return chains


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def merge(opened, resolved, patch):
    """Apply changed threads: {"resolved": true} moves one to the resolved list, false reopens it."""
    o = {t["id"]: t for t in opened}
    r = {t["id"]: t for t in resolved}
    for p in patch:
        tid = p["id"]
        if p.get("resolved") is True:
            base = o.pop(tid, None) or r.get(tid) or {}
            r[tid] = {"id": tid, "title": p.get("title") or base.get("title") or "Untitled thread",
                      "cat": p.get("cat") or base.get("cat") or "ideas", "icon": p.get("icon") or base.get("icon"),
                      "active": p.get("active") or base.get("active"), "resolvedAt": p.get("resolvedAt") or now()}
        else:
            base = o.get(tid) or r.pop(tid, None) or {"prev": None, "cat": "ideas"}
            base.pop("resolvedAt", None)
            base.update({k: v for k, v in p.items() if k != "resolved"})
            o[tid] = base
    return list(o.values()), list(r.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("threads", help="open threads JSON")
    ap.add_argument("out")
    ap.add_argument("--resolved", help="resolved threads JSON: [{id, title, cat, icon, resolvedAt}]")
    ap.add_argument("--patch", help="JSON list of changed threads; both input files are rewritten")
    a = ap.parse_args()
    opened = [t for t in json.load(open(a.threads)) if not t.get("resolved")]
    resolved = json.load(open(a.resolved)) if a.resolved and os.path.exists(a.resolved) else []
    if a.patch:
        opened, resolved = merge(opened, resolved, json.load(open(a.patch)))
        json.dump(opened, open(a.threads, "w"), ensure_ascii=False)
        if a.resolved:
            json.dump(resolved, open(a.resolved, "w"), ensure_ascii=False)
    # A thread in both lists (snapshots taken at different times) goes with its newest event.
    res_at = {t["id"]: t.get("resolvedAt") or "" for t in resolved}
    act_at = {t["id"]: t.get("active") or "" for t in opened}
    both = res_at.keys() & act_at.keys()
    opened = [t for t in opened if not (t["id"] in both and res_at[t["id"]] >= act_at[t["id"]])]
    resolved = [t for t in resolved if not (t["id"] in both and res_at[t["id"]] < act_at[t["id"]])]
    chains = build(opened)
    resolved.sort(key=lambda t: t.get("resolvedAt") or "", reverse=True)
    doc = {"updatedAt": now(), "open": len(opened),
           "chains": [{"id": cid, **body} for cid, body in chains.items()],
           "resolved": resolved[:300]}
    json.dump(doc, open(a.out, "w"), ensure_ascii=False)
    print(json.dumps({"open": doc["open"], "chains": len(doc["chains"]), "resolved": len(doc["resolved"]),
                      "bytes": os.path.getsize(a.out)}))


if __name__ == "__main__":
    main()
