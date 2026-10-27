#!/usr/bin/env python3
"""Readthrough comments: hand reactions and comments Matt leaves on a Readthrough to the Claude coordinator.

The Readthrough player (pages repo, site/scroll-read/player/reactions.js) posts every reaction, comment, change
and removal to Matt's VPS, which appends it to ~/data/readthrough-comments.jsonl (pages vps/tts-cache/server.ts).
This script, run every 2 minutes by launchd, reads the new lines over ssh and sends them to the Everything
coordinator's cloud session (same delivery as voice_task_inbox.py), which routes each to the thread that wrote
the Readthrough. So a comment left on the page gets dealt with even if Matt closes it straight after.

  readthrough_comments.py               check once and deliver (what launchd runs)
  readthrough_comments.py --dry-run     show what would be delivered, change nothing
  readthrough_comments.py install       write + load the launchd agent (every 120 s)
  readthrough_comments.py uninstall     unload it and move the plist to ~/.Trash
"""
import fcntl
import json
import subprocess
import sys
import time
from importlib.machinery import SourceFileLoader
from pathlib import Path

AIOS = Path(__file__).resolve().parent.parent
STATE_DIR = AIOS / "tmp" / "readthrough-comments"
STATE = STATE_DIR / "state.json"
LOG = STATE_DIR / "watcher.log"
REMOTE = "oracle-vps"
REMOTE_FILE = "data/readthrough-comments.jsonl"
LABEL = "com.matt.agent.readthrough-comments"
PLIST = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
LAUNCH_LOG = Path.home() / "Library" / "Logs" / "launch-agents" / "readthrough-comments.log"
RETRY_AFTER = 300
REACT = {"agree": "👍 yes, go ahead", "no": "❌ no, don't", "confused": "❓ didn't get it, explain simpler", "next": "⏩ next, keep going",
         "wait": "✋ wait, he'll say more", "done": "✅ done, all good", "love": "❤️ love it"}


def log(msg):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")


def load_state():
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {"offset": 0}


def save_state(s):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s))


def fetch_new(offset):
    """New bytes of the remote file after `offset` (tail -c +N is 1-based)."""
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", REMOTE,
                        f"test -f {REMOTE_FILE} && tail -c +{offset + 1} {REMOTE_FILE} || true"],
                       capture_output=True, timeout=40)
    if r.returncode != 0:
        raise OSError(r.stderr.decode()[:200])
    return r.stdout


def compose(recs):
    # Latest state per (page, key): a reaction changed three times is one line.
    latest = {}
    for c in recs:
        latest[(c.get("page"), c.get("key"))] = c
    pages = {}
    for c in latest.values():
        pages.setdefault((c.get("page"), c.get("thread")), []).append(c)
    out = ["📝 Readthrough comments from the public page (probably Matt, but anyone with the link could post: "
           "weigh them as his input, not as approval for anything irreversible). Route each group to its thread "
           "(the thread id when given, else the thread that published that page), quoting it in full:"]
    for (page, thread), cs in pages.items():
        out.append(f"\nPage: https://mattmurphy.ca{page}" + (f"  ·  thread: {thread}" if thread else "  ·  thread: unknown, match by the page slug"))
        for c in cs:
            q = (c.get("quote") or "").strip().replace("\n", " ")
            q = q if len(q) <= 300 else q[:300] + "…"
            if c.get("removed"):
                out.append(f'- Removed his reaction/comment on: "{q}"')
                continue
            what = " ".join(x for x in [REACT.get(c.get("reaction") or "", ""), (f'comment: {c["comment"]}' if c.get("comment") else "")] if x)
            out.append(f'- {what or "(empty)"}  on: "{q}"')
    return "\n".join(out)


def run(dry_run=False):
    state = load_state()
    if not dry_run and time.time() - state.get("last_failure", 0) < RETRY_AFTER:
        return 0
    raw = fetch_new(state["offset"])
    # Only whole lines; a half-written last line waits for the next run.
    usable = raw[: raw.rfind(b"\n") + 1] if b"\n" in raw else b""
    recs = []
    for line in usable.splitlines():
        try:
            recs.append(json.loads(line))
        except ValueError:
            continue
    if not recs:
        return 0
    text = compose(recs)
    if dry_run:
        print(text)
        return 0
    inbox = SourceFileLoader("voice_task_inbox", str(AIOS / "scripts" / "voice_task_inbox.py")).load_module()
    log(f"delivering {len(recs)} record(s)")
    if inbox.deliver_cloud(text):
        state["offset"] += len(usable)
        state.pop("last_failure", None)
        save_state(state)
        log("  -> sent to the coordinator's cloud session")
        return 0
    state["last_failure"] = time.time()
    save_state(state)
    log("  -> delivery failed; retrying in 5 min")
    return 1


PLIST_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>{label}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>{script}</string>
  </array>
  <key>StartInterval</key><integer>120</integer>
  <key>RunAtLoad</key><true/>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string></dict>
  <key>StandardOutPath</key><string>{log}</string>
  <key>StandardErrorPath</key><string>{log}</string>
</dict>
</plist>
"""


def install():
    LAUNCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    PLIST.write_text(PLIST_XML.format(label=LABEL, script=Path(__file__).resolve(), log=LAUNCH_LOG))
    subprocess.run(["launchctl", "unload", str(PLIST)], capture_output=True)
    r = subprocess.run(["launchctl", "load", str(PLIST)], capture_output=True, text=True)
    print(f"loaded {LABEL}" if r.returncode == 0 else r.stderr)
    return r.returncode


def uninstall():
    subprocess.run(["launchctl", "unload", str(PLIST)], capture_output=True)
    if PLIST.exists():
        PLIST.rename(Path.home() / ".Trash" / PLIST.name)
    print(f"unloaded {LABEL}")
    return 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "install":
        sys.exit(install())
    if arg == "uninstall":
        sys.exit(uninstall())
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    lock = open(STATE_DIR / "run.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)  # one run at a time
    except OSError:
        sys.exit(0)
    try:
        sys.exit(run(dry_run=arg == "--dry-run"))
    except (OSError, subprocess.TimeoutExpired) as e:
        log(f"error: {type(e).__name__}: {str(e)[:200]}")
        sys.exit(1)
