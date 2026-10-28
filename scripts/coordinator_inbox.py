#!/usr/bin/env python3
"""Coordinator inbox: hand messages (voice tasks) to Matt's Code-tab Coordinator session.

The Coordinator is a desktop Code-tab session; nothing outside the app can type into it.
So scripts drop messages into an outbox folder, and the context-alert mod, running inside
the Coordinator session, polls this script every 30 s and submits each message as a prompt.
The mod also touches a heartbeat, so senders know whether the Coordinator is listening.

  coordinator_inbox.py claim            this session ($CLAUDE_CODE_SESSION_ID) becomes the Coordinator
  coordinator_inbox.py who              print the Coordinator's session id
  coordinator_inbox.py alive            exit 0 if the Coordinator's mod polled in the last 3 min
  coordinator_inbox.py put < text       queue a message for the Coordinator
  coordinator_inbox.py poll <session>   (the mod) heartbeat + print and take pending messages as JSON
  coordinator_inbox.py tweaks           (the mod) print context-alert's tweak values as JSON, seeding the file
"""
import json
import os
import sys
import time
from pathlib import Path

AIOS = Path(__file__).resolve().parent.parent
SESSION_FILE = AIOS / "coordinator" / "session.txt"  # CLI session id (the transcript's uuid)
BOX = AIOS / "tmp" / "coordinator-inbox"
OUTBOX = BOX / "pending"
DONE = BOX / "delivered"
HEARTBEAT = BOX / "alive"
ALIVE_SEC = 180

TWEAKS = Path.home() / ".hammerspoon" / "tweaks" / "context_alert.json"
REGISTRY = Path.home() / ".hammerspoon" / "tweaks_registry.json"
KNOBS = {
    "compact.idleMinutes": {"default": 50, "min": 10, "max": 58, "step": 1,
                            "note": "Minutes idle before a big thread compacts itself (the cache lasts 60)"},
    "compact.minTokens": {"default": 200000, "min": 50000, "max": 600000, "step": 10000,
                          "note": "Smallest context (tokens) worth compacting while idle"},
    "hold.minTokens": {"default": 250000, "min": 0, "max": 1000000, "step": 10000,
                       "note": "A message into a cold thread is held only above this size; smaller ones just resume"},
}


def who():
    try:
        return SESSION_FILE.read_text().strip()
    except OSError:
        return ""


def alive():
    try:
        return time.time() - HEARTBEAT.stat().st_mtime < ALIVE_SEC
    except OSError:
        return False


def put(text):
    OUTBOX.mkdir(parents=True, exist_ok=True)
    name = f"{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}.txt"
    tmp = OUTBOX / f".{name}"
    tmp.write_text(text)
    tmp.rename(OUTBOX / name)  # atomic: the poller never sees half a message
    return OUTBOX / name


def poll(session):
    if not session or session != who():
        return {"coordinator": False}
    BOX.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.touch()
    DONE.mkdir(parents=True, exist_ok=True)
    messages = []
    for f in sorted(OUTBOX.glob("*.txt")) if OUTBOX.exists() else []:
        try:
            messages.append(f.read_text())
            f.rename(DONE / f.name)
        except OSError:
            continue
    return {"coordinator": True, "messages": messages}


def tweaks():
    """Seed missing knobs into the tweaks file (and the panel's registry); print current values."""
    try:
        doc = json.loads(TWEAKS.read_text())
    except (OSError, ValueError):
        doc = {}
    doc.setdefault("app", "Context alert (Claude threads)")
    knobs = doc.setdefault("tweaks", {})
    changed = not TWEAKS.exists()
    for key, spec in KNOBS.items():
        k = knobs.setdefault(key, {"value": spec["default"]})
        for field in ("min", "max", "step", "note"):
            k.setdefault(field, spec[field])
        if k.get("default") != spec["default"]:
            k["default"] = spec["default"]
            changed = True
    if changed or any(key not in knobs for key in KNOBS):
        TWEAKS.parent.mkdir(parents=True, exist_ok=True)
        TWEAKS.write_text(json.dumps(doc, indent=2) + "\n")
    try:
        reg = json.loads(REGISTRY.read_text())
        if reg.setdefault("apps", {}).get(doc["app"]) != str(TWEAKS):
            reg["apps"][doc["app"]] = str(TWEAKS)
            REGISTRY.write_text(json.dumps(reg, indent=2) + "\n")
    except (OSError, ValueError):
        pass
    return {key: knobs[key].get("value", KNOBS[key]["default"]) for key in KNOBS}


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "claim":
        sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
        if not sid:
            print("no CLAUDE_CODE_SESSION_ID: run this from inside the Coordinator session", file=sys.stderr)
            return 1
        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        SESSION_FILE.write_text(sid + "\n")
        print(f"Coordinator is now {sid}")
        return 0
    if cmd == "who":
        print(who())
        return 0
    if cmd == "alive":
        return 0 if alive() else 1
    if cmd == "put":
        print(put(sys.stdin.read()))
        return 0
    if cmd == "poll":
        print(json.dumps(poll(argv[2] if len(argv) > 2 else "")))
        return 0
    if cmd == "tweaks":
        print(json.dumps(tweaks()))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
