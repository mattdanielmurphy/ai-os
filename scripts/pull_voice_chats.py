#!/usr/bin/env python3
"""Pull Matt's Claude voice-chat transcripts from claude.ai into his Obsidian vault, nightly.

Safety net for the connector's save_call: voice Claude may forget to save a call, so this
copies every voice conversation (claude.ai marks them platform == "VOICE") updated since the
last run to `Voice calls/Transcripts/` in the vault, where QMD indexes them for every agent.
Calls that never ran save_call are handed to the project coordinator to file facts and act on
to-dos.

How: claude.ai has no public chat-history API, so this reads its internal one through Matt's
signed-in Chrome via the browser-use CDP daemon (same as scripts/youtube.sh). Read-only. If
claude.ai changes that API, this logs an error and does nothing else.

  pull_voice_chats.py              pull new/updated voice chats (what launchd runs at 3:30)
  pull_voice_chats.py --since 7d   re-pull the last 7 days
  pull_voice_chats.py --dry-run    list what it would save
  pull_voice_chats.py install      write + load the launchd agent
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

AIOS = Path.home() / "projects" / "ai-os"
VAULT = Path.home() / "Library" / "Mobile Documents" / "iCloud~md~obsidian" / "Documents" / "Personal"
OUT = VAULT / "Voice calls" / "Transcripts"
STATE = AIOS / "tmp" / "voice-chats" / "state.json"
LOG = AIOS / "tmp" / "voice-chats" / "pull.log"
QUEUE = AIOS / "tmp" / "voice-task-inbox" / "queue"
WATCHER = AIOS / "scripts" / "voice_task_inbox.py"
LABEL = "com.matt.agent.voice-chat-pull"
PLIST = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
PATH = f"{Path.home()}/.bun/bin:{Path.home()}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Runs inside `browser-use` (helpers list_tabs/new_tab/switch_tab/js are pre-imported).
BROWSER = r'''
import json, time
tabs = [t for t in list_tabs() if t["url"].startswith("https://claude.ai")]
opened = None
if tabs:
    switch_tab(tabs[0]["targetId"])
else:
    opened = new_tab("https://claude.ai/recents")
    time.sleep(5)
SINCE = __SINCE__
r = js("""(async()=>{
  const orgs = await (await fetch('/api/organizations', {credentials:'include'})).json();
  if (!Array.isArray(orgs)) return {error: 'not signed in to claude.ai'};
  const org = orgs.find(o => (o.capabilities||[]).includes('chat')) || orgs[0];
  const base = `/api/organizations/${org.uuid}/chat_conversations`;
  const voice = [];
  for (let offset = 0; offset < 1000; offset += 50) {
    const page = await (await fetch(`${base}?limit=50&offset=${offset}`, {credentials:'include'})).json();
    if (!Array.isArray(page) || !page.length) break;
    for (const c of page) if (c.platform === 'VOICE' && c.updated_at >= '""" + SINCE + """') voice.push(c);
    if (page[page.length-1].updated_at < '""" + SINCE + """') break;
  }
  const out = [];
  for (const c of voice) {
    const d = await (await fetch(`${base}/${c.uuid}?tree=True&rendering_mode=messages&render_all_tools=true`, {credentials:'include'})).json();
    out.push({uuid: c.uuid, name: c.name, created_at: c.created_at, updated_at: c.updated_at,
      messages: (d.chat_messages||[]).map(m => ({sender: m.sender, at: m.created_at,
        blocks: (m.content||[]).map(b => ({type: b.type, text: b.text || '', name: b.name || ''}))}))});
  }
  return {voice: out};
})()""")
print("RESULT" + json.dumps(r))
'''


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")


def fetch(since_iso):
    script = BROWSER.replace("__SINCE__", json.dumps(since_iso))
    r = subprocess.run(["uvx", "--from", "browser-use", "browser-use"], input=script, capture_output=True,
                       text=True, timeout=600, env=dict(os.environ, PATH=PATH))
    line = next((l for l in r.stdout.splitlines() if l.startswith("RESULT")), None)
    if not line:
        raise RuntimeError(f"browser-use gave no result (exit {r.returncode}): {(r.stderr or r.stdout)[-300:]}")
    data = json.loads(line[6:])
    if not isinstance(data, dict) or "voice" not in data:
        raise RuntimeError(f"claude.ai: {str(data)[:300]}")
    return data["voice"]


def local_day(iso):
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.astimezone().strftime("%Y-%m-%d %H%M")


def render(c):
    title = re.sub(r'[\\/:*?"<>|#^\[\]]', "", c["name"] or "Voice chat").strip()[:60] or "Voice chat"
    lines = ["---", f"title: {json.dumps(title)}", f"created: {c['created_at'][:10]}", f"updated: {c['updated_at'][:10]}",
             "type: daily", "tags: [journal, ai-os]", "source: voice-chat-transcript", f"claude_uuid: {c['uuid']}", "---", "",
             f"# {title}", "", f"Voice chat on claude.ai: https://claude.ai/chat/{c['uuid']}", ""]
    saved = False
    for m in c["messages"]:
        who = "**Matt:**" if m["sender"] == "human" else "**Claude:**"
        parts = []
        for b in m["blocks"]:
            if b["type"] == "text" and b["text"].strip():
                parts.append(b["text"].strip())
            elif b["type"] == "tool_use" and b["name"]:
                parts.append(f"_(used {b['name']})_")
                saved = saved or b["name"].endswith("save_call")
        if parts:
            lines += [f"{who} " + "\n\n".join(parts), ""]
    return title, "\n".join(lines), saved


def queue_review(unsaved):
    QUEUE.mkdir(parents=True, exist_ok=True)
    body = ("These voice calls ended without save_call. Read each transcript, file any new facts about Matt "
            "or his setup, and act on reminders, calendar events or emails he asked for (use the _review-voice-calls skill):\n"
            + "\n".join(f"- {p}" for p in unsaved) + "\n\nUrgent: no")
    (QUEUE / f"{int(time.time() * 1000)}-voicepull.json").write_text(json.dumps({"title": "Review unsaved voice calls", "body": body}))
    subprocess.Popen(["/usr/bin/python3", str(WATCHER)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def run(since=None, dry_run=False):
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    if since is None:
        since = state.get("last_pull") or (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    convs = fetch(since)
    saved_paths, unsaved = [], []
    seen = state.setdefault("reviewed", {})
    for c in convs:
        title, md, had_save = render(c)
        name = f"{local_day(c['created_at'])} {title} [{c['uuid'][:8]}].md"
        rel = f"Voice calls/Transcripts/{name}"
        if dry_run:
            print(f"{'saved-by-call' if had_save else 'UNSAVED      '} {rel} ({len(c['messages'])} msgs)")
            continue
        OUT.mkdir(parents=True, exist_ok=True)
        for old in OUT.glob(f"* [{c['uuid'][:8]}].md"):  # the title can change between pulls
            if old.name != name:
                old.rename(Path.home() / ".Trash" / old.name)
        (OUT / name).write_text(md)
        saved_paths.append(rel)
        if not had_save and seen.get(c["uuid"]) != c["updated_at"]:
            unsaved.append(rel)
        seen[c["uuid"]] = c["updated_at"]
    if dry_run:
        print(f"{len(convs)} voice chat(s) since {since}")
        return 0
    if unsaved:
        queue_review(unsaved)
    if saved_paths:
        subprocess.Popen(["qmd", "update"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         env=dict(os.environ, PATH=PATH), start_new_session=True)
    state["last_pull"] = started
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1))
    log(f"pulled {len(saved_paths)} voice chat(s) since {since}; {len(unsaved)} sent for review")
    return 0


PLIST_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>{label}</string>
  <key>ProgramArguments</key>
  <array><string>/usr/bin/python3</string><string>{script}</string></array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>3</integer><key>Minute</key><integer>30</integer></dict>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>{path}</string></dict>
  <key>StandardOutPath</key><string>{log}</string>
  <key>StandardErrorPath</key><string>{log}</string>
</dict>
</plist>
"""


def install():
    launch_log = Path.home() / "Library" / "Logs" / "launch-agents" / "voice-chat-pull.log"
    launch_log.parent.mkdir(parents=True, exist_ok=True)
    PLIST.write_text(PLIST_XML.format(label=LABEL, script=Path(__file__).resolve(), path=PATH, log=launch_log))
    subprocess.run(["launchctl", "unload", str(PLIST)], capture_output=True)
    r = subprocess.run(["launchctl", "load", str(PLIST)], capture_output=True, text=True)
    print(f"loaded {LABEL} (daily 3:30)" if r.returncode == 0 else r.stderr)
    return r.returncode


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["install"]:
        sys.exit(install())
    since = None
    if "--since" in args:
        n = args[args.index("--since") + 1]
        since = (datetime.now(timezone.utc) - timedelta(days=int(n.rstrip("d")))).strftime("%Y-%m-%dT%H:%M:%S")
    try:
        sys.exit(run(since, dry_run="--dry-run" in args))
    except Exception as e:
        log(f"error: {type(e).__name__}: {str(e)[:300]}")
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
