#!/usr/bin/env python3
"""
sync_antigravity_ide.py
Safely syncs Antigravity.app threads and brain directories into Antigravity IDE.
Formats trajectory summaries into the exact native Topic -> DataEntry Protobuf envelope
expected by Antigravity IDE's TrajectorySummariesLifecycle.
"""

import os
import sys
import glob
import shutil
import sqlite3
import base64
import subprocess
from pathlib import Path

SOURCE_GEMINI = Path.home() / ".gemini" / "antigravity"
TARGET_GEMINI = Path.home() / ".gemini" / "antigravity-ide"
TARGET_APP_SUPPORT = Path.home() / "Library" / "Application Support" / "Antigravity IDE" / "User" / "globalStorage"
STATE_DB = TARGET_APP_SUPPORT / "state.vscdb"
CANARY_DB = TARGET_APP_SUPPORT / "state.vscdb.canary_bak"
BACKUP_DIR = Path.home() / ".gemini" / "backups" / "antigravity_ide_sync"


def is_ide_running() -> bool:
    try:
        out = subprocess.check_output(["pgrep", "-fi", "Antigravity IDE"], text=True)
        return bool(out.strip())
    except subprocess.CalledProcessError:
        return False


def encode_varint(n: int) -> bytes:
    res = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            res.append(b | 0x80)
        else:
            res.append(b)
            break
    return bytes(res)


def parse_entries(raw_bytes: bytes) -> dict:
    """Parses repeated DataEntry payloads from a Topic protobuf message."""
    entries = {}
    i = 0
    while i < len(raw_bytes):
        if i >= len(raw_bytes):
            break
        tag = raw_bytes[i]
        if tag != 0x0A:  # Field 1 wire 2 (Topic.entries)
            break
        i += 1
        length = 0
        shift = 0
        while True:
            b = raw_bytes[i]
            i += 1
            length |= (b & 0x7F) << shift
            if not (b & 0x80):
                break
            shift += 7
        entry_payload = raw_bytes[i : i + length]
        i += length

        sub_i = 0
        if sub_i < len(entry_payload) and entry_payload[sub_i] == 0x0A:
            sub_i += 1
            k_len = 0
            k_shift = 0
            while True:
                kb = entry_payload[sub_i]
                sub_i += 1
                k_len |= (kb & 0x7F) << k_shift
                if not (kb & 0x80):
                    break
                k_shift += 7
            key = entry_payload[sub_i : sub_i + k_len].decode("utf-8", errors="ignore")
            entries[key] = entry_payload
    return entries


def build_topic_envelope(entries: dict) -> bytes:
    """Constructs the canonical Topic message from dictionary of DataEntry payloads."""
    out = bytearray()
    for k, payload in entries.items():
        migrated = payload.replace(b"/Users/matthewmurphy/", b"/Users/matt/")
        out.extend(b"\x0a" + encode_varint(len(migrated)) + migrated)
    return bytes(out)


def sync_threads(force: bool = False, limit: int = 0):
    print("=== Antigravity IDE Thread Synchronizer ===")
    if is_ide_running() and not force:
        print("[WARNING] Antigravity IDE is currently running.")
        print("Please close Antigravity IDE before synchronizing to prevent database lock conflicts.")
        print("Run with --force to override if needed.")
        return False

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_DB.exists():
        shutil.copy2(STATE_DB, BACKUP_DIR / "state.vscdb.pre_sync")
        print(f"Backed up state.vscdb to {BACKUP_DIR / 'state.vscdb.pre_sync'}")

    # 1. Symlink conversation files (.db) and brain folders
    TARGET_GEMINI.mkdir(parents=True, exist_ok=True)
    (TARGET_GEMINI / "conversations").mkdir(parents=True, exist_ok=True)
    (TARGET_GEMINI / "brain").mkdir(parents=True, exist_ok=True)

    src_convs = glob.glob(str(SOURCE_GEMINI / "conversations" / "*.db"))
    linked_conv = 0
    for f in src_convs:
        target = TARGET_GEMINI / "conversations" / os.path.basename(f)
        if not target.exists():
            os.symlink(f, target)
            linked_conv += 1

    src_brains = [
        d
        for d in os.listdir(SOURCE_GEMINI / "brain")
        if (SOURCE_GEMINI / "brain" / d).is_dir() and not d.startswith(".")
    ]
    linked_brain = 0
    for d in src_brains:
        target = TARGET_GEMINI / "brain" / d
        if not target.exists():
            os.symlink(SOURCE_GEMINI / "brain" / d, target)
            linked_brain += 1

    print(f"Linked {linked_conv} conversation DBs and {linked_brain} brain directories.")

    # 2. Collect trajectory summaries from canary backup and agyhub_summaries_proto.pb
    all_entries = {}

    pb_path = SOURCE_GEMINI / "agyhub_summaries_proto.pb"
    if pb_path.exists():
        pb_entries = parse_entries(pb_path.read_bytes())
        all_entries.update(pb_entries)
        print(f"Extracted {len(pb_entries)} trajectory summaries from {pb_path.name}.")

    if CANARY_DB.exists():
        try:
            con_can = sqlite3.connect(CANARY_DB)
            row = con_can.cursor().execute(
                "SELECT value FROM ItemTable WHERE key = 'antigravityUnifiedStateSync.trajectorySummaries'"
            ).fetchone()
            if row and row[0]:
                can_entries = parse_entries(base64.b64decode(row[0]))
                all_entries.update(can_entries)
                print(f"Merged {len(can_entries)} trajectory summaries from canary_bak.")
            con_can.close()
        except Exception as e:
            print(f"Warning reading canary_bak: {e}")

    if limit > 0 and len(all_entries) > limit:
        all_entries = dict(list(all_entries.items())[:limit])

    topic_bytes = build_topic_envelope(all_entries)
    topic_b64 = base64.b64encode(topic_bytes).decode("utf-8")
    print(f"Constructed canonical Topic envelope with {len(all_entries)} entries ({len(topic_bytes)} bytes).")

    # 3. Migrate sidebar workspaces
    sidebar_b64 = None
    if CANARY_DB.exists():
        try:
            con_can = sqlite3.connect(CANARY_DB)
            w_row = con_can.cursor().execute(
                "SELECT value FROM ItemTable WHERE key = 'antigravityUnifiedStateSync.sidebarWorkspaces'"
            ).fetchone()
            if w_row and w_row[0]:
                w_bytes = base64.b64decode(w_row[0]).replace(b"/Users/matthewmurphy/", b"/Users/matt/")
                sidebar_b64 = base64.b64encode(w_bytes).decode("utf-8")
            con_can.close()
        except Exception as e:
            print(f"Warning reading sidebarWorkspaces: {e}")

    # 4. Write to state.vscdb
    con = sqlite3.connect(STATE_DB)
    cur = con.cursor()
    cur.execute("PRAGMA integrity_check")
    cur.execute(
        "INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)",
        ("antigravityUnifiedStateSync.trajectorySummaries", topic_b64),
    )
    if sidebar_b64:
        cur.execute(
            "INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)",
            ("antigravityUnifiedStateSync.sidebarWorkspaces", sidebar_b64),
        )
    con.commit()
    cur.execute("PRAGMA wal_checkpoint(FULL)")
    con.close()
    print("[SUCCESS] Successfully synchronized trajectory summaries into Antigravity IDE state.vscdb!")
    return True


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    sync_threads(force=force_flag)
