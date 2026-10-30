#!/usr/bin/env python3
"""Stop hook: block a reply that promises future behaviour when no rule was saved.

Matt, 2026-10-29: the Coordinator said "I'll link everything I mention from now on" and saved
nothing. If the last reply promises future behaviour and no rule/memory file changed in the
last few minutes, the stop is blocked once with a reason. Fails open.
"""
import json
import re
import sys
import time
from pathlib import Path

HOME = Path.home()
RECENT_S = 15 * 60  # a rule file touched this recently counts as saved this turn
PROMISE = re.compile(
    r"\b(from now on,? I(?:'ll| will)|I(?:'ll| will) (?:remember|keep that in mind|make sure to)|"
    r"going forward,? I|in (?:the )?future,? I(?:'ll| will)|I won'?t (?:do that |forget )?again|"
    r"noted for next time|next time I(?:'ll| will))",
    re.I,
)
RULE_PLACES = [
    HOME / "projects/ai-os/.rules",
    HOME / ".claude/CLAUDE.md",
    HOME / ".claude/projects",  # memory dirs
    HOME / "projects/slub-hq/setup/core.md",
]


def last_reply(data: dict) -> str:
    msg = data.get("last_assistant_message")
    if msg:
        return msg if isinstance(msg, str) else json.dumps(msg)
    lines = Path(data["transcript_path"]).read_text().splitlines()
    for line in reversed(lines[-200:]):
        e = json.loads(line)
        if e.get("type") == "assistant":
            parts = e.get("message", {}).get("content", [])
            text = " ".join(p.get("text", "") for p in parts if isinstance(p, dict))
            if text.strip():
                return text
    return ""


def rule_saved() -> bool:
    cutoff = time.time() - RECENT_S
    for p in RULE_PLACES:
        if not p.exists():
            continue
        files = [p] if p.is_file() else (
            p.glob("*/memory/*.md") if p.name == "projects" else p.rglob("*.md"))
        if any(f.stat().st_mtime > cutoff for f in files):
            return True
    return False


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("stop_hook_active"):
        return
    m = PROMISE.search(last_reply(data))
    if not m or rule_saved():
        return
    print(json.dumps({"decision": "block", "reason": (
        f'Your reply promises future behaviour ("{m.group(0)}") but no rule file changed. '
        "You are ephemeral: a promise is not saved. Add a rule to ai-os `.rules/*.md`, run "
        "`python3 ~/projects/ai-os/scripts/build_rules.py`, commit and push, then say in one line "
        "what was saved. If it truly was a one-off, reword the reply.")}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
