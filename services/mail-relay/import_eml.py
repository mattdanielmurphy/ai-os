#!/usr/bin/env python3
"""Copy old mail (a Zoho export: .eml files or .zip of them) into the new mailbox.

Each subfolder of the export becomes a folder under "Zoho/" (e.g. Zoho/Inbox).
Safe to re-run: messages whose Message-ID is already in the target folder are
skipped. Original dates and read state (as Seen) are kept.

Uses the same env vars as relay.py (IMAP_HOST, MAIL_USER, MAIL_PASSWORD, ...).
  python3 import_eml.py <export.zip | folder> [--prefix Zoho] [--dry-run]
"""

import argparse
import email
import email.policy
import imaplib
import os
import sys
import time
import zipfile
from email.utils import parsedate_to_datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relay  # noqa: E402


def iter_eml(src):
    """Yield (subfolder, raw bytes) for every .eml in a zip or directory."""
    p = Path(src)
    if p.is_file() and zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as z:
            for n in sorted(z.namelist()):
                if n.lower().endswith(".eml"):
                    parent = str(Path(n).parent)
                    yield ("" if parent == "." else parent), z.read(n)
    else:
        for f in sorted(p.rglob("*.eml")):
            parent = str(f.parent.relative_to(p))
            yield ("" if parent == "." else parent), f.read_bytes()


def existing_ids(c, folder):
    typ, _ = c.select(relay.quoted(folder), readonly=True)
    if typ != "OK":
        c.create(relay.quoted(folder))
        return set()
    typ, data = c.uid("SEARCH", None, "ALL")
    uids = data[0].split() if data and data[0] else []
    ids = set()
    for i in range(0, len(uids), 200):
        typ, d = c.uid("FETCH", b",".join(uids[i:i + 200]).decode(), "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])")
        for part in d:
            if isinstance(part, tuple):
                mid = email.message_from_bytes(part[1]).get("Message-ID")
                if mid:
                    ids.add(mid.strip())
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--prefix", default="Zoho")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    c = None if args.dry_run else relay.imap()
    seen = {}
    added = skipped = 0
    for sub, raw in iter_eml(args.src):
        folder = "/".join(x for x in (args.prefix, sub.replace("\\", "/")) if x) or "INBOX"
        m = email.message_from_bytes(raw, policy=email.policy.default)
        mid = (m.get("Message-ID") or "").strip()
        if args.dry_run:
            print(f"{folder}: {m.get('Subject', '')}")
            added += 1
            continue
        if folder not in seen:
            seen[folder] = existing_ids(c, folder)
        if mid and mid in seen[folder]:
            skipped += 1
            continue
        try:
            when = parsedate_to_datetime(m.get("Date")).timestamp()
        except Exception:
            when = time.time()
        typ, data = c.append(relay.quoted(folder), "(\\Seen)", imaplib.Time2Internaldate(when), raw)
        if typ != "OK":
            print(f"FAILED {folder}: {m.get('Subject', '')}: {data}", file=sys.stderr)
            continue
        if mid:
            seen[folder].add(mid)
        added += 1
    if c:
        c.logout()
    print(f"{'would add' if args.dry_run else 'added'} {added}, skipped {skipped} already there")


if __name__ == "__main__":
    main()
