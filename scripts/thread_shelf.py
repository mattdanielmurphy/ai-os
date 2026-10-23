#!/usr/bin/env python3
"""Turn a thread snapshot into Everything Shelf documents (the live threads overview artifact).

The shelf page (https://claude.ai/artifact/6Ei7CuXHVYeHvsx94yQH4o) reads its threads from its artifact
database. Only Claude can read project threads (hearthbot tools), so a Claude session gathers
a snapshot and this script shapes it into the one document the page reads, `shelf/current`:

  python3 scripts/thread_shelf.py <threads.json> <out.json> [--patch changed.json]
  then ArtifactData set collection "shelf", doc_id "current", file_path <out.json>, if_version <current>

threads.json: [{"id", "title", "bucket", "active", "last": {"by", "at", "text"}, "prev", "cat", "resolved"?}]
  open threads; "prev" = cmsg id this thread was handed off from, or null.
One document (not one per chain) so a refresh is a single pinned write. The page also writes
`requests/<thread id>` docs ({action: "resolve"}) that the refreshing session applies and deletes.
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
            "active": t.get("active"), "last": t.get("last"), "threads": links,
        }
    return chains


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("threads")
    ap.add_argument("out")
    ap.add_argument("--patch", help="JSON list of changed threads; merged by id into <threads.json>, which is rewritten")
    a = ap.parse_args()
    threads = json.load(open(a.threads))
    if a.patch:
        by_id = {t["id"]: t for t in threads}
        for p in json.load(open(a.patch)):
            by_id.setdefault(p["id"], {"prev": None, "cat": "ideas"}).update(p)
        threads = [t for t in by_id.values() if not t.get("resolved")]
        json.dump(threads, open(a.threads, "w"), ensure_ascii=False)
    threads = [t for t in threads if not t.get("resolved")]
    chains = build(threads)
    doc = {"updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "open": len(threads), "chains": [{"id": cid, **body} for cid, body in chains.items()]}
    json.dump(doc, open(a.out, "w"), ensure_ascii=False)
    print(json.dumps({"open": doc["open"], "chains": len(doc["chains"]), "bytes": os.path.getsize(a.out)}))


if __name__ == "__main__":
    main()
