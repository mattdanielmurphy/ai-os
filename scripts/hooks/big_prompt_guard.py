#!/usr/bin/env python3
"""UserPromptSubmit hook: hand huge prompts to the Coordinator to a dedicated sub-coordinator.

Matt, 2026-10-29: the Coordinator's context is full of other work, so a very long
message gets better handling in a fresh thread whose only job is to act as
coordinator for it (split it into asks and spawn threads). Applies only in the
Coordinator session (`coordinator/session.txt`). The word threshold rises when
weekly usage runs hot (`claude_pace.py`), and the hook is off when the pace says Sonnet.
Fails open: any error means no extra context.
"""
import json
import subprocess
import sys
from pathlib import Path

AIOS = Path.home() / "projects/ai-os"
# Feel knobs: words that trigger the hand-off, per usage-pace verdict (pace exit code).
THRESHOLD_BY_PACE = {0: 500, 1: 900, 2: None, 3: 500}  # OPUS, CAREFUL, SONNET (off), pace error
PACE_TIMEOUT_S = 6


def pace_code() -> int:
    try:
        return subprocess.run(
            ["python3", str(AIOS / "scripts/claude_pace.py")],
            capture_output=True, timeout=PACE_TIMEOUT_S,
        ).returncode
    except Exception:
        return 3


def main() -> None:
    data = json.load(sys.stdin)
    coord = (AIOS / "coordinator/session.txt").read_text().strip()
    if data.get("session_id") != coord:
        return
    prompt = data.get("prompt", "")
    if prompt.lstrip().startswith("/"):
        return
    words = len(prompt.split())
    if words < min(t for t in THRESHOLD_BY_PACE.values() if t):
        return
    code = pace_code()
    limit = THRESHOLD_BY_PACE.get(code)
    if not limit or words < limit:
        return
    note = (
        f"Big prompt ({words} words, threshold {limit} at the current usage pace). "
        "Don't plan this in your own crowded context. Save Matt's message verbatim to "
        "`docs/coordinator/asks/<date>-<slug>.md`, then start ONE fresh sub-coordinator "
        "thread (Opus, medium effort; low if the pace says CAREFUL) told to ACT AS COORDINATOR "
        "for that file: split it into separate asks and return an action list (per ask: a thread "
        "title, model, effort and self-contained brief, or a quick step for you), never doing the "
        "work itself. (Sessions started by a session can't start threads, so it returns the list.) "
        "Tell Matt in one line with its link; when the list arrives, offer one Actions button to "
        "start them all. "
        "Skip this only if the message is mostly pasted material with a short ask."
    )
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit", "additionalContext": note}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
