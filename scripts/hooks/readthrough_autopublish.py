#!/usr/bin/env python3
"""PostToolUse hook: publish a details file as a Readthrough whenever an agent writes it.

Agents never run `pages readthrough` themselves (Matt, 2026-10-29: "Readthrough shouldn't cost the
agents ANYTHING"). On a Write/Edit (or a Bash command naming) ~/projects/ai-os/docs/details/*.md this hook returns at once and
leaves a detached worker that waits until the file has been quiet for QUIET seconds (so several edits
in one reply make one publish), then runs `pages readthrough`. Publishing does no TTS: the voice is
made per paragraph the first time someone presses play, then cached on the VPS.

The link is predictable, so agents write it without waiting:
  https://mattmurphy.ca/claude/<project>/<file name without .md and without its YYYY-MM-DD- prefix>
Project: a `<!-- readthrough project=NAME -->` line in the file wins; else `code` in Code-tab sessions
(CLAUDE_CODE_HOST_SESSION_ID=local_…), else `everything`.

Fails open: any error is logged to tmp/readthrough-autopublish.log and the agent never sees it.
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

AIOS = Path.home() / "projects" / "ai-os"
DETAILS = AIOS / "docs" / "details"
LOG = AIOS / "tmp" / "readthrough-autopublish.log"
PAGES = Path.home() / ".local" / "bin" / "pages"
QUIET = 20


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


def project_for(path: Path, host: str) -> str:
    m = re.search(r"<!--\s*readthrough\s+project=([a-z0-9-]+)\s*-->", path.read_text(errors="ignore"))
    if m:
        return m.group(1)
    return "code" if host.startswith("local_") else "everything"


def worker(path: Path, host: str, sid: str = ""):
    # Debounce: wait until the file stops changing, and let only the newest worker publish.
    stamp = path.with_name(f".{path.name}.readthrough")
    me = str(os.getpid())
    stamp.write_text(me)
    while True:
        time.sleep(QUIET)
        if not stamp.exists() or stamp.read_text() != me:
            return
        if time.time() - path.stat().st_mtime >= QUIET:
            break
    stamp.unlink(missing_ok=True)
    args = [str(PAGES), "readthrough", str(path), "--project", project_for(path, host)]
    if re.fullmatch(r"(cmsg|local|session|cse)_[A-Za-z0-9-]+", host):
        args += ["--cmsg", host]
    r = subprocess.run(args, capture_output=True, text=True, timeout=300)
    log(f"{'ok' if r.returncode == 0 else 'FAILED'} {path.name}: {(r.stdout + r.stderr).strip()[-400:]}")
    url = next((l for l in r.stdout.splitlines() if l.startswith("https://")), "")
    if r.returncode == 0 and url and sid:
        # Tell the Hammerspoon Readthrough float (modules/readthrough_float.lua) which thread it belongs to.
        try:
            subprocess.run(["/usr/local/bin/hs", "-c", f'require("modules.readthrough_float").published({json.dumps(url)}, {json.dumps(sid)})'],
                           capture_output=True, timeout=10)
        except Exception as e:
            log(f"float: {e!r}")


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "--worker":
        return worker(Path(sys.argv[2]), sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    data = json.load(sys.stdin)
    ti = data.get("tool_input") or {}
    p = ti.get("file_path") or ""
    if not p:  # a Bash append like `cat >> …/docs/details/x.md`
        m = re.search(r"[\w~/.-]*docs/details/[\w.-]+\.md", ti.get("command") or "")
        p = m.group(0) if m else ""
    path = Path(p).expanduser().resolve() if p else None
    if not path or path.parent != DETAILS.resolve() or path.suffix != ".md" or not path.exists():
        return
    host = os.environ.get("CLAUDE_CODE_HOST_SESSION_ID", "")
    subprocess.Popen([sys.executable, __file__, "--worker", str(path), host, data.get("session_id") or ""],
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # fail open
        try:
            log(f"error: {e!r}")
        except Exception:
            pass
    sys.exit(0)
