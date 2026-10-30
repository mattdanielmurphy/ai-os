#!/usr/bin/env python3
"""Claude weekly usage + pace, from the CodexBar CLI (claude.ai usage API).

Prints weekly % used, where an even pace would be by now, and a model call:
  OPUS    weekly use within 2 points of even pace: Opus is fine
  CAREFUL up to 5 points over pace: Opus only for hard work
  SONNET  more than 5 points over pace (or session window nearly full)

Usage: claude_pace.py [--json]
Exit code: 0 OPUS, 1 CAREFUL, 2 SONNET, 3 error (CodexBar missing/failed).
Needs CodexBar (brew install --cask steipete/tap/codexbar) signed in to claude.ai.
"""
import json, shutil, subprocess, sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Edmonton")
ON_PACE_SLACK = 2     # points over even pace that still count as on pace (CodexBar shows these as "on pace")
CAREFUL_OVER = 5      # points over even pace before saying Sonnet
SESSION_FULL = 85     # 5-hour window % that forces Sonnet for now


def fetch():
    exe = shutil.which("codexbar") or "/opt/homebrew/bin/codexbar"  # launchd PATH lacks brew
    out = subprocess.run([exe, "usage", "--provider", "claude", "--json"],
                         capture_output=True, text=True, timeout=60).stdout
    return json.loads(out)[0]


def even_pace(win, now):
    reset = datetime.fromisoformat(win["resetsAt"].replace("Z", "+00:00"))
    left = (reset - now).total_seconds() / 60
    return max(0.0, min(100.0, 100 * (1 - left / win["windowMinutes"]))), reset


def main():
    try:
        d = fetch()
        week, session = d["usage"]["secondary"], d["usage"]["primary"]
    except Exception as e:
        print(f"ERROR: couldn't read Claude usage from CodexBar ({e})", file=sys.stderr)
        return 3
    now = datetime.now(timezone.utc)
    expected, reset = even_pace(week, now)
    used = week["usedPercent"]
    over = used - expected
    if over > CAREFUL_OVER or session["usedPercent"] >= SESSION_FULL:
        call, code = "SONNET", 2
    elif over > ON_PACE_SLACK:
        call, code = "CAREFUL", 1
    else:
        call, code = "OPUS", 0
    info = {
        "call": call, "weekly_used": used, "weekly_expected": round(expected),
        "over_pace": round(over), "session_used": session["usedPercent"],
        "weekly_resets": reset.astimezone(TZ).strftime("%a %b %-d %-I:%M%p"),
        "plan": d["usage"].get("loginMethod"),
        "codexbar_summary": d.get("pace", {}).get("secondary", {}).get("summary"),
    }
    if "--json" in sys.argv:
        print(json.dumps(info))
    else:
        side = "over" if over > 0 else "under"
        print(f"{call}: weekly {used}% used, even pace {info['weekly_expected']}% "
              f"({abs(info['over_pace'])} pts {side}); 5h session {info['session_used']}%; "
              f"resets {info['weekly_resets']}")
    return code


if __name__ == "__main__":
    sys.exit(main())
