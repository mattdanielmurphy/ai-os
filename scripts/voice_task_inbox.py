#!/usr/bin/env python3
"""Voice task inbox: pass tasks that voice Claude emails to Matt over to the project coordinator.

Voice Claude (Claude app voice chat) can't reach the Everything project directly; it can
only send email from Matt's Gmail. So it emails Matt's own address with the subject
`[Claude task] <title>`. This script, run every minute by launchd, finds those emails in
Gmail over IMAP, pastes them into the project chat (where the coordinator picks them up)
with the same Hammerspoon path Hey Claude uses, then moves the emails to Gmail Trash.

Only mail that Matt's own account SENT counts (Gmail "in:sent"), so a stranger emailing
him a "[Claude task]" subject can't inject tasks.

  voice_task_inbox.py               check once and deliver (what launchd runs)
  voice_task_inbox.py --dry-run     list pending tasks, deliver and delete nothing
  voice_task_inbox.py install       write + load the launchd agent (every 60s)
  voice_task_inbox.py uninstall     unload it and move the plist to ~/.Trash

Needs GMAIL_ADDRESS and GMAIL_APP_PASSWORD (a Google app password) in ~/projects/ai-os/.env.
Spec voice Claude follows: docs/VOICE_TASKS.md.
"""
import email
import email.header
import email.policy
import email.utils
import imaplib
import json
import re
import subprocess
import sys
import time
from importlib.machinery import SourceFileLoader
from pathlib import Path

AIOS = Path(__file__).resolve().parent.parent
ENV_FILE = Path.home() / "projects" / "ai-os" / ".env"
STATE_DIR = AIOS / "tmp" / "voice-task-inbox"
STATE = STATE_DIR / "state.json"
LOG = STATE_DIR / "watcher.log"
LABEL = "com.matt.agent.voice-task-inbox"
PLIST = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
LAUNCH_LOG = Path.home() / "Library" / "Logs" / "launch-agents" / "voice-task-inbox.log"

SUBJECT_TAG = "[Claude task]"
SEARCH = '"in:sent subject:(Claude task)"'  # Gmail search; exact tag re-checked below
RETRY_AFTER = 300   # seconds to wait after a cancelled or failed delivery
MAX_BODY = 4000     # chars per task pasted into the chat


def log(msg):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")


def load_env():
    """Read the two Gmail keys from .env without echoing anything."""
    keys = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            m = re.match(r"\s*(?:export\s+)?(GMAIL_ADDRESS|GMAIL_APP_PASSWORD)\s*=\s*(.*)$", line)
            if m:
                keys[m.group(1)] = m.group(2).strip().strip("'\"")
    return keys.get("GMAIL_ADDRESS", ""), keys.get("GMAIL_APP_PASSWORD", "").replace(" ", "")


def load_state():
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {}


def save_state(state):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1))


def decode(value):
    return str(email.header.make_header(email.header.decode_header(value or ""))).strip()


def plain_body(msg):
    part = msg.get_body(preferencelist=("plain", "html"))
    if part is None:
        return ""
    text = part.get_content()
    if part.get_content_type() == "text/html":
        text = re.sub(r"<br\s*/?>|</p>", "\n", text, flags=re.I)
        text = re.sub(r"<[^>]+>", "", text)
    # Drop quoted history if voice Claude replied in a thread.
    text = re.split(r"\n\s*On .{5,200} wrote:\s*\n", text)[0]
    return re.sub(r"\n{3,}", "\n\n", text).strip()[:MAX_BODY]


def parse_task(raw, address):
    """(title, body) for a task email from `address`, else None."""
    msg = email.message_from_bytes(raw, policy=email.policy.default)
    subject = decode(msg["Subject"])
    sender = email.utils.parseaddr(decode(msg["From"]))[1].lower()
    if not subject.startswith(SUBJECT_TAG) or sender != address.lower():
        return None
    return subject[len(SUBJECT_TAG):].strip() or "(no title)", plain_body(msg)


def special_folder(imap, flag):
    _, rows = imap.list()
    for row in rows or []:
        line = row.decode(errors="replace")
        if flag in line:
            return line.rsplit(' "/" ', 1)[-1].strip()
    return None


def fetch_tasks(imap, address):
    """Return [(uid, title, body)] for pending task emails, oldest first."""
    _, data = imap.uid("SEARCH", "X-GM-RAW", SEARCH)
    tasks = []
    for uid in (data[0] or b"").split():
        _, parts = imap.uid("FETCH", uid, "(BODY.PEEK[])")
        raw = next((p[1] for p in parts if isinstance(p, tuple)), None)
        task = parse_task(raw, address) if raw else None
        if task:
            tasks.append((uid, *task))
    return tasks


def compose(tasks):
    head = "Voice task from voice chat" if len(tasks) == 1 else f"{len(tasks)} voice tasks from voice chat"
    blocks = []
    for i, (_, title, body) in enumerate(tasks, 1):
        label = title if len(tasks) == 1 else f"{i}. {title}"
        blocks.append(f"{label}\n{body}".strip())
    return f"🎙️ {head}:\n\n" + "\n\n".join(blocks)


def screen_locked():
    out = subprocess.run(["ioreg", "-n", "Root", "-d1", "-a"], capture_output=True, text=True).stdout
    return "CGSSessionScreenIsLocked" in out


def deliver(text):
    """Paste into the Everything project chat via Hey Claude's Hammerspoon path."""
    hey = SourceFileLoader("hey_claude", str(AIOS / "bin" / "hey-claude")).load_module()
    return hey.send_to_claude(text, True)


def run(dry_run=False):
    address, password = load_env()
    state = load_state()
    if not address or not password:
        if dry_run:
            print("missing GMAIL_ADDRESS or GMAIL_APP_PASSWORD in ~/projects/ai-os/.env")
        elif not state.get("warned_missing"):  # once, not every minute
            log("missing GMAIL_ADDRESS or GMAIL_APP_PASSWORD in .env; waiting for them")
            state["warned_missing"] = True
            save_state(state)
        return 0
    state.pop("warned_missing", None)
    if not dry_run and time.time() - state.get("last_failure", 0) < RETRY_AFTER:
        return 0
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        imap.login(address, password)
        all_mail = special_folder(imap, "\\All")
        trash = special_folder(imap, "\\Trash")
        if not all_mail or not trash:
            log("couldn't find Gmail's All Mail / Trash folders")
            return 1
        imap.select(all_mail)
        tasks = fetch_tasks(imap, address)
        if dry_run:
            print(f"{len(tasks)} pending task(s)")
            for _, title, body in tasks:
                print(f"- {title}\n  {body[:300]!r}")
            return 0
        if not tasks:
            return 0
        if screen_locked():
            return 0  # the paste needs an unlocked screen; try again next minute
        log(f"delivering {len(tasks)} task(s): {[t[1] for t in tasks]}")
        if not deliver(compose(tasks)):
            state["last_failure"] = time.time()
            save_state(state)
            log("  -> delivery failed or cancelled; retrying in 5 min")
            return 1
        state.pop("last_failure", None)
        save_state(state)
        for uid, _, _ in tasks:
            typ, _ = imap.uid("MOVE", uid, trash)
            if typ != "OK":
                log(f"  -> couldn't trash uid {uid.decode()}")
        log("  -> sent to the project chat; emails moved to Trash")
        return 0
    finally:
        try:
            imap.logout()
        except Exception:
            pass


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
  <key>StartInterval</key><integer>60</integer>
  <key>RunAtLoad</key><true/>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
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
    try:
        sys.exit(run(dry_run=arg == "--dry-run"))
    except (imaplib.IMAP4.error, OSError) as e:
        log(f"error: {type(e).__name__}: {str(e)[:200]}")
        sys.exit(1)
