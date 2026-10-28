#!/usr/bin/env python3
"""Voice task inbox: pass tasks that voice Claude emails to Matt over to his coordinator.

Since 2026-10-27 tasks go first to the Code-tab Coordinator (scripts/coordinator_inbox.py, picked up
by the context-alert mod inside that session); the Everything project routes below are fallbacks.

Voice Claude (Claude app voice chat) can't reach the Everything project directly; it can
only send email from Matt's Gmail. So it emails Matt's own address with the subject
`[Claude task] <title>`. This script, run every minute by launchd, finds those emails in
Gmail over IMAP, pastes them into the project chat (where the coordinator picks them up)
then moves the emails to Gmail Trash. Delivery goes straight into the coordinator's cloud
session with `claude -p --cloud <id>` (no screen takeover, works while locked); the old
Hammerspoon paste (Hey Claude's path) is the fallback when that fails, e.g. after the
coordinator is recycled and its id in COORD_FILE goes stale.

Only mail that Matt's own account SENT counts (Gmail "in:sent", re-checked through the
\\Sent label), so a stranger emailing him a "[Claude task]" subject can't inject tasks. The
From address isn't checked: Gmail may send as an alias (matt@ his domain).

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
import fcntl
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
QUEUE = STATE_DIR / "queue"          # tasks from the Mac connector (services/mac-connector)
QUEUE_DONE = STATE_DIR / "delivered"
LOG = STATE_DIR / "watcher.log"
COORD_FILE = AIOS / "config" / "coordinator_session.txt"  # Everything coordinator's cse_ id
LABEL = "com.matt.agent.voice-task-inbox"
PLIST = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
LAUNCH_LOG = Path.home() / "Library" / "Logs" / "launch-agents" / "voice-task-inbox.log"

SUBJECT_TAG = "[Claude task]"
GMAIL_LABEL = "Claude tasks"
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
    text = part.get_content().replace("\r\n", "\n")
    if part.get_content_type() == "text/html":
        text = re.sub(r"<br\s*/?>|</p>", "\n", text, flags=re.I)
        text = re.sub(r"<[^>]+>", "", text)
    # Drop quoted history if voice Claude replied in a thread.
    text = re.split(r"\n\s*On .{5,200} wrote:\s*\n", text)[0]
    return re.sub(r"\n{3,}", "\n\n", text).strip()[:MAX_BODY]


def parse_task(raw):
    """(title, body) for a task email, else None."""
    msg = email.message_from_bytes(raw, policy=email.policy.default)
    subject = decode(msg["Subject"])
    if not subject.startswith(SUBJECT_TAG):
        return None
    return subject[len(SUBJECT_TAG):].strip() or "(no title)", plain_body(msg)


def special_folder(imap, flag):
    _, rows = imap.list()
    for row in rows or []:
        line = row.decode(errors="replace")
        if flag in line:
            return line.rsplit(' "/" ', 1)[-1].strip()
    return None


def fetch_tasks(imap):
    """Return [(uid, title, body)] for pending task emails, oldest first."""
    _, data = imap.uid("SEARCH", "X-GM-RAW", SEARCH)
    tasks = []
    for uid in (data[0] or b"").split():
        _, parts = imap.uid("FETCH", uid, "(X-GM-LABELS BODY.PEEK[])")
        part = next((p for p in parts if isinstance(p, tuple)), None)
        if not part or b"\\Sent" not in part[0]:
            continue
        task = parse_task(part[1])
        if task:
            tasks.append((uid, *task))
    return tasks


def queued_tasks():
    """[(path, title, body)] written by the Mac connector's send_task, oldest first."""
    tasks = []
    for f in sorted(QUEUE.glob("*.json")) if QUEUE.exists() else []:
        try:
            d = json.loads(f.read_text())
            tasks.append((f, str(d.get("title") or "(no title)"), str(d.get("body") or "")[:MAX_BODY]))
        except (OSError, ValueError):
            continue
    return tasks


def compose(tasks):
    head = "Voice task from voice chat" if len(tasks) == 1 else f"{len(tasks)} voice tasks from voice chat"
    blocks = []
    for i, (_, title, body) in enumerate(tasks, 1):
        label = title if len(tasks) == 1 else f"{i}. {title}"
        blocks.append(f"{label}\n{body}".strip())
    reply = ('When each one is done, report back to voice chat: '
             'python3 ~/projects/ai-os/scripts/voice_reply.py "<title>" "<one-line result>"')
    return f"🎙️ {head}:\n\n" + "\n\n".join(blocks) + "\n\n" + reply


def screen_locked():
    out = subprocess.run(["/usr/sbin/ioreg", "-n", "Root", "-d1", "-a"], capture_output=True, text=True).stdout
    return "CGSSessionScreenIsLocked" in out


def coordinator_id():
    try:
        sid = COORD_FILE.read_text().strip()
    except OSError:
        return ""
    return sid if re.fullmatch(r"(cse|session)_[A-Za-z0-9]+", sid) else ""


def deliver_coordinator(text):
    """Queue the task for the Code-tab Coordinator (its mod submits it within 30 s). True if it's listening."""
    inbox = AIOS / "scripts" / "coordinator_inbox.py"
    if subprocess.run(["python3", str(inbox), "alive"]).returncode != 0:
        log("  -> Coordinator's mod hasn't polled in 3 min; trying the old routes")
        return False
    r = subprocess.run(["python3", str(inbox), "put"], input=text, capture_output=True, text=True)
    return r.returncode == 0


def deliver_cloud(text):
    """Queue the task into the coordinator's cloud session; no screen input. True on success."""
    sid = coordinator_id()
    if not sid:
        return False
    try:
        r = subprocess.run(["claude", "-p", "--cloud", sid, "--output-format", "json"],
                           input=text, capture_output=True, text=True, timeout=90)
        out = (r.stdout.strip().splitlines() or [""])[-1]
        if json.loads(out).get("ok") is True:
            return True
        why = (r.stderr or r.stdout).strip()
    except (OSError, subprocess.TimeoutExpired, ValueError) as e:
        why = f"{type(e).__name__}: {e}"
    log(f"  -> cloud send to {sid} failed: {why[:200]}")
    return False


def deliver_paste(text):
    """Paste into the Everything project chat via Hey Claude's Hammerspoon path."""
    hey = SourceFileLoader("hey_claude", str(AIOS / "bin" / "hey-claude")).load_module()
    shown = hey.notify
    hey.notify = lambda msg: (log(f"  -> {msg}"), shown(msg))  # keep the failure reason
    return hey.send_to_claude(text, True)


def gmail_tasks(address, password, dry_run):
    """Open Gmail, tidy task emails out of the inbox, return (imap, trash, [(uid, title, body)])."""
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(address, password)
    all_mail = special_folder(imap, "\\All")
    trash = special_folder(imap, "\\Trash")
    if not all_mail or not trash:
        log("couldn't find Gmail's All Mail / Trash folders")
        return imap, None, []
    imap.select(all_mail)
    tasks = fetch_tasks(imap)
    if not dry_run:
        for uid, _, _ in tasks:  # what a Gmail filter would do: out of the inbox, into the label
            imap.uid("STORE", uid, "+X-GM-LABELS", f'("{GMAIL_LABEL}")')
            imap.uid("STORE", uid, "-X-GM-LABELS", "(\\Inbox)")
    return imap, trash, tasks


def run(dry_run=False):
    state = load_state()
    address, password = load_env()
    imap, trash, mail = None, None, []
    if address and password:
        state.pop("warned_missing", None)
        try:
            imap, trash, mail = gmail_tasks(address, password, dry_run)
        except (imaplib.IMAP4.error, OSError) as e:
            log(f"gmail error: {type(e).__name__}: {str(e)[:200]}")
    elif not state.get("warned_missing"):  # once, not every minute
        log("missing GMAIL_ADDRESS or GMAIL_APP_PASSWORD in .env; only connector tasks will be delivered")
        state["warned_missing"] = True
        save_state(state)
    try:
        queued = queued_tasks()
        tasks = queued + mail
        if dry_run:
            print(f"{len(tasks)} pending task(s)")
            for _, title, body in tasks:
                print(f"- {title}\n  {body[:300]!r}")
            return 0
        if not tasks or time.time() - state.get("last_failure", 0) < RETRY_AFTER:
            return 0
        log(f"delivering {len(tasks)} task(s): {[t[1] for t in tasks]}")
        text = compose(tasks)
        if deliver_coordinator(text):
            route = "Code-tab Coordinator"
        elif deliver_cloud(text):
            route = "coordinator's cloud session"
        elif screen_locked():
            return 0  # the paste fallback needs an unlocked screen; retry next minute
        else:
            # No idle wait (Matt, 2026-10-21): the take-control banner warns him first (Esc cancels) and
            # hey_claude never pastes into a project chat box that holds his draft.
            route = "project chat (paste fallback)"
            if not deliver_paste(text):
                route = ""
        if not route:
            state["last_failure"] = time.time()
            save_state(state)
            log("  -> delivery failed or cancelled; retrying in 5 min")
            return 1
        state.pop("last_failure", None)
        save_state(state)
        QUEUE_DONE.mkdir(parents=True, exist_ok=True)
        for f, _, _ in queued:
            f.rename(QUEUE_DONE / f.name)
        for uid, _, _ in mail:
            typ, _ = imap.uid("MOVE", uid, trash)
            if typ != "OK":
                log(f"  -> couldn't trash uid {uid.decode()}")
        log(f"  -> sent to the {route}; emails moved to Trash")
        return 0
    finally:
        if imap:
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
    except (imaplib.IMAP4.error, OSError) as e:
        log(f"error: {type(e).__name__}: {str(e)[:200]}")
        sys.exit(1)
