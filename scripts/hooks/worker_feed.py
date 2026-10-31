#!/usr/bin/env python3
"""UserPromptSubmit hook: every message Matt types in a worker reaches its coordinator's queue.

In a worker: returns at once and forks `feed`, which confirms in the transcript that a human
typed it (the hook payload can't tell Matt from a SendMessage peer), appends it to
tmp/coordinator-inbox/workers/<coordinator>.jsonl, then asks Haiku if it is out of the thread's
scope. Only a likely out-of-scope message wakes the coordinator, through coordinator_inbox.put.
In a coordinator: drains its queue into the turn as additionalContext. Never costs a coordinator
a turn otherwise. Fails open: any error means no output.
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

AIOS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AIOS / "scripts"))
import coordinator_inbox as inbox  # noqa: E402

QUEUE = inbox.BOX / "workers"
LOG = inbox.BOX / "worker-feed.log"
MAX_CONTEXT = 6000
MAX_MESSAGE = 2000
CONFIRM_TRIES = 8  # transcript line can land a little after the hook
CONFIRM_WAIT_S = 1.5
CLASSIFY_TIMEOUT_S = 45


def log(line):
    QUEUE.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"{time.strftime('%F %T')} {line}\n")


def registry():
    try:
        return json.loads((AIOS / "coordinator" / "threads.json").read_text())["threads"]
    except (OSError, ValueError, KeyError):
        return []


def coordinators(threads):
    return {t["id"]: t for t in threads if t.get("role") in ("central", "project-coordinator")}


def route(worker_id, cwd, threads):
    """(coordinator id, worker's registry entry). A project coordinator beats a stale central
    `coordinator` field: chain `glass-tv-home` belongs to project `glass-tv`."""
    coords = coordinators(threads)
    if worker_id in coords:
        return "", None
    me = next((t for t in threads if t.get("id") == worker_id), None)
    projects = [c for c in coords.values() if c.get("project")]
    chain = (me or {}).get("chain") or ""
    for c in projects:
        if chain == c["project"] or chain.startswith(c["project"] + "-"):
            return c["id"], me
    if me and me.get("coordinator") in coords:
        return me["coordinator"], me
    if me and me.get("parent") in coords:
        return me["parent"], me
    for c in projects:
        if f"/projects/{c['project']}" in (cwd + "/"):
            return c["id"], me
    return "", me


def human_text(transcript, prompt):
    """The typed text if the newest real user entry is a human's matching `prompt`, else ''."""
    probe = prompt.strip()[:80]
    with open(transcript, "rb") as f:
        f.seek(0, 2)
        f.seek(max(0, f.tell() - 30_000_000))  # a pasted image makes one line megabytes long
        lines = f.read().decode("utf-8", "ignore").splitlines()
    for line in reversed(lines):
        if '"user"' not in line or probe[:20].replace('"', '') not in line.replace('\\"', ''):
            continue
        try:
            j = json.loads(line)
        except ValueError:
            continue
        if j.get("type") != "user" or j.get("isMeta") or j.get("isSidechain"):
            continue
        content = j.get("message", {}).get("content")
        parts = [content] if isinstance(content, str) else [
            b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        if any("You are a session started from another session" in p for p in parts):
            return ""  # a spawn brief is stamped human but a session wrote it
        typed = "\n".join(p for p in parts if not p.lstrip().startswith("<system-reminder>")).strip()
        if probe not in typed and typed[:80] not in prompt:
            continue
        return typed if (j.get("origin") or {}).get("kind") == "human" else ""
    return None  # not written yet


def classify(title, asked, text):
    """Haiku's one-line reason if `text` looks out of scope for the thread, else ''."""
    ask = (
        f"A worker thread is titled {title!r}, with job: {asked!r}.\n"
        "Its owner typed the message below. Answer with one line of JSON only: "
        '{"out_of_scope": true|false, "reason": "<under 12 words>"}. '
        "out_of_scope=true only if it is a new task unrelated to this job or for a different project. "
        "Follow-ups, feedback, corrections, questions and short replies are in scope.\n\n<message>\n"
        + text[:MAX_MESSAGE] + "\n</message>"
    )
    QUEUE.mkdir(parents=True, exist_ok=True)
    run = subprocess.run(
        [shutil.which("claude") or "/opt/homebrew/bin/claude", "-p", "--model", "haiku", "--setting-sources", "", "--no-session-persistence", "--tools", ""],
        input=ask, capture_output=True, text=True, timeout=CLASSIFY_TIMEOUT_S, cwd=str(QUEUE),
    )
    out = run.stdout
    verdict = json.loads(out[out.index("{"): out.rindex("}") + 1])
    return (verdict.get("reason") or "looks out of scope") if verdict.get("out_of_scope") else ""


def wake(coordinator, central, title, worker_id, text, reason):
    note = (
        f"📥 Possibly out of scope: Matt typed this in worker [{title}](#{worker_id}) ({reason}):\n\n"
        f"{text[:MAX_MESSAGE]}\n\nDecide per the worker-feed section of your coordinator doc."
    )
    if inbox.alive(coordinator):
        inbox.put(note, None if coordinator == central else coordinator)
        return "woke"
    if coordinator != central:  # a project coordinator with no live mod: the front desk steps in
        inbox.put(f"(Its coordinator {coordinator} is not running.)\n{note}")
        return "woke central"
    inbox.put(note)  # central's outbox persists until its mod polls
    return "queued for central"


def feed(payload):
    threads = registry()
    worker_id = inbox.desktop_id(payload.get("session_id", ""))
    if not worker_id:
        return
    coordinator, me = route(worker_id, payload.get("cwd", ""), threads)
    if not coordinator:
        return
    prompt, typed = payload.get("prompt", ""), None
    for _ in range(CONFIRM_TRIES):
        time.sleep(CONFIRM_WAIT_S)
        typed = human_text(payload.get("transcript_path", ""), prompt)
        if typed is not None:
            break
    if not typed:
        return
    title = (me or {}).get("title") or inbox.desktop_title(worker_id) or worker_id
    asked = (me or {}).get("asked") or title
    QUEUE.mkdir(parents=True, exist_ok=True)
    with (QUEUE / f"{coordinator}.jsonl").open("a") as f:
        f.write(json.dumps({"at": time.strftime("%H:%M"), "id": worker_id, "title": title,
                            "text": typed[:MAX_MESSAGE]}) + "\n")
    log(f"queued {worker_id} -> {coordinator}")
    if len(typed.split()) < inbox.tweaks()["workerFeed.minWords"]:
        return
    reason = classify(title, asked, typed)
    if reason:
        central = next((t["id"] for t in threads if t.get("role") == "central"), "")
        log(f"flagged {worker_id}: {reason}: {wake(coordinator, central, title, worker_id, typed, reason)}")


def drain(coordinator):
    src = QUEUE / f"{coordinator}.jsonl"
    if not src.exists():
        return ""
    taking = src.with_suffix(f".{time.time_ns()}.taking")
    src.rename(taking)  # appends after this start a new file
    entries = [json.loads(line) for line in taking.read_text().splitlines() if line.strip()]
    with (QUEUE / "delivered.jsonl").open("a") as f:
        f.write(taking.read_text())
    taking.unlink()
    lines = [f"- {e['at']} [{e['title']}](#{e['id']}): {e['text']}" for e in entries]
    body = "\n".join(lines)
    if len(body) > MAX_CONTEXT:
        body = body[-MAX_CONTEXT:] + "\n(older ones cut; full text in tmp/coordinator-inbox/workers/delivered.jsonl)"
    return ("Matt typed these directly in your worker threads since your last turn. They are for awareness "
            "(no reply needed); flag any that are out of scope per your coordinator doc.\n" + body)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "feed":
        feed(json.load(sys.stdin))
        return
    raw = sys.stdin.read()
    payload = json.loads(raw)
    local = inbox.desktop_id(payload.get("session_id", ""))
    threads = registry()
    if local in coordinators(threads):
        note = drain(local)
        if note:
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit", "additionalContext": note}}))
        return
    child = subprocess.Popen([sys.executable, __file__, "feed"], stdin=subprocess.PIPE, text=True,
                             stdout=subprocess.DEVNULL, stderr=(QUEUE.mkdir(parents=True, exist_ok=True) or LOG.open("a")),
                             start_new_session=True)
    child.stdin.write(raw)
    child.stdin.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        try:
            log(f"error {e!r}")
        except OSError:
            pass
