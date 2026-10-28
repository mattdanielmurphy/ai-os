#!/usr/bin/env python3
"""UserPromptSubmit hook: tell every Claude session about Matt's live (or just-ended) call.

While call-transcript is running, adds the transcript path and its latest lines to each prompt,
so a question asked mid-call is read against the call. For 3 hours after a call ends, points at
the saved transcript instead. Silent otherwise. Written by scripts/call-transcript.
"""
import os
import time
from pathlib import Path

CALLS = Path.home() / "calls"
PID, CUR, LAST = CALLS / ".transcript.pid", CALLS / ".transcript.current", CALLS / ".transcript.last"
TAIL = 60
STALE_S = 10 * 60  # no new transcript line for this long = the call is over


def running() -> bool:
    try:
        os.kill(int(PID.read_text().strip()), 0)
        return True
    except Exception:
        return False


def main():
    md = Path(CUR.read_text().strip()) if CUR.exists() else None
    # A recorder left running after the call keeps its pid alive; only fresh lines mean a live call.
    if running() and md and md.exists() and time.time() - md.stat().st_mtime < STALE_S:
        lines = [l for l in md.read_text(errors="ignore").splitlines() if l.startswith("[")]
        print(f"LIVE CALL IN PROGRESS. Matt is on a call right now; the transcript updates live at {md} "
              f"(re-read it for anything newer). Assume his message is about this call unless it clearly "
              f"isn't, and weigh the most recent lines most. Last {min(TAIL, len(lines))} lines:")
        print("\n".join(lines[-TAIL:]) or "(nothing said yet)")
    elif md and md.exists() and time.time() - md.stat().st_mtime < 3 * 3600:
        print(f"Matt just finished a call; the full transcript is at {md}. "
              f"If his message seems to be about it, read that file first.")
    elif LAST.exists() and time.time() - LAST.stat().st_mtime < 3 * 3600:
        print(f"Matt just finished a call; the full transcript is at {LAST.read_text().strip()}. "
              f"If his message seems to be about it, read that file first.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
