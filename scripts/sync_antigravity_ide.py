#!/usr/bin/env python3
"""
sync_antigravity_ide.py
Safely syncs Antigravity.app threads and brain directories into Antigravity IDE.
Formats trajectory summaries into the exact Topic -> Row (Base64) Protobuf envelope
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


def encode_length_delimited(tag: int, data: bytes) -> bytes:
    tag_byte = (tag << 3) | 2
    return encode_varint(tag_byte) + encode_varint(len(data)) + data


def encode_row(b64_val_str: str) -> bytes:
    # Row: field 1 = string (value)
    return encode_length_delimited(1, b64_val_str.encode("utf-8"))


def encode_data_entry(key: str, row_bytes: bytes) -> bytes:
    # DataEntry: field 1 = string (key), field 2 = Row (message)
    key_bytes = key.encode("utf-8")
    entry_payload = encode_length_delimited(1, key_bytes) + encode_length_delimited(2, row_bytes)
    return entry_payload


def encode_topic(data_map: dict) -> bytes:
    # Topic: field 1 = repeated DataEntry
    out = bytearray()
    for k, b64_str in data_map.items():
        row_bytes = encode_row(b64_str)
        entry_payload = encode_data_entry(k, row_bytes)
        out.extend(encode_length_delimited(1, entry_payload))
    return bytes(out)


def parse_chunks(data: bytes) -> dict:
    i = 0
    chunks = {}
    while i < len(data):
        tag = data[i]
        if tag != 0x0A:
            break
        i += 1
        l = 0
        s = 0
        while True:
            b = data[i]
            i += 1
            l |= (b & 0x7F) << s
            if not (b & 0x80):
                break
            s += 7
        chunk = data[i : i + l]
        i += l

        sub_i = 0
        if len(chunk) > 2 and chunk[sub_i] == 0x0A:
            sub_i += 1
            sl = 0
            ss = 0
            while True:
                sb = chunk[sub_i]
                sub_i += 1
                sl |= (sb & 0x7F) << ss
                if not (sb & 0x80):
                    break
                ss += 7
            k = chunk[sub_i : sub_i + sl].decode("utf-8", errors="ignore")
            chunks[k] = chunk
    return chunks


def sync_threads(force: bool = False, limit: int = 500):
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

    # 2. Extract and format summary topic
    summaries_pb = SOURCE_GEMINI / "agyhub_summaries_proto.pb"
    if not summaries_pb.exists():
        print(f"[ERROR] Summaries file {summaries_pb} not found.")
        return False

    with open(summaries_pb, "rb") as fp:
        raw_pb = fp.read()

    chunks = parse_chunks(raw_pb)
    print(f"Extracted {len(chunks)} trajectory summaries from source protobuf.")

    # Map to Base64 rows (most recent first or capped to limit)
    data_map = {}
    items = list(chunks.items())
    if limit and len(items) > limit:
        items = items[:limit]

    for k, chunk in items:
        migrated = chunk.replace(b"/Users/matthewmurphy/", b"/Users/matt/")
        data_map[k] = base64.b64encode(migrated).decode("utf-8")

    topic_bytes = encode_topic(data_map)
    topic_b64 = base64.b64encode(topic_bytes).decode("utf-8")
    print(f"Constructed Topic envelope with {len(data_map)} entries ({len(topic_bytes)} bytes).")

    # 3. Write to state.vscdb
    con = sqlite3.connect(STATE_DB)
    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)",
        ("antigravityUnifiedStateSync.trajectorySummaries", topic_b64),
    )
    con.commit()
    con.close()
    print("[SUCCESS] Successfully synchronized trajectory summaries into Antigravity IDE state.vscdb!")
    return True


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    sync_threads(force=force_flag)
