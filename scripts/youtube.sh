#!/usr/bin/env bash
# Play / pause / check a YouTube video in Matt's Chrome without keypresses or focus changes.
# Usage: scripts/youtube.sh [play|pause|toggle|status]   (default: play)
#
# How: talks to Chrome over CDP via the browser-use daemon (`uvx --from browser-use browser-use`),
# which reuses the already-approved debugging connection, so no "Allow remote debugging?" prompt.
# AppleScript `execute javascript` is off in Chrome, so it is only used to read tab URLs.
# Target: a playing video for pause/toggle; otherwise the YouTube tab showing in the front-most
# Chrome window that has one, else the first YouTube tab. play/pause ~2s; status can be slow
# (background tabs Chrome has frozen take ~5s each to time out).
set -euo pipefail
action="${1:-play}"

# URLs of each window's active tab, front window first.
active_urls="$(osascript -e 'set out to ""
if application "Google Chrome" is running then
tell application "Google Chrome" to repeat with w in windows
set out to out & (URL of active tab of w) & linefeed
end repeat
end if
return out' 2>/dev/null || true)"

ACTION="$action" ACTIVE_URLS="$active_urls" uvx --from browser-use browser-use <<'PY'
import os
action = os.environ["ACTION"]
active = [u for u in os.environ["ACTIVE_URLS"].splitlines() if u]
tabs = [t for t in list_tabs() if "youtube.com/watch" in t["url"]]
if not tabs:
    print("no YouTube tab open"); raise SystemExit(1)

STATE = "(()=>{const v=document.querySelector('video');return v?[v.paused,Math.round(v.currentTime),Math.round(v.duration)]:null})()"
def state(t):
    switch_tab(t["targetId"])
    try: return js(STATE)
    except Exception: return None  # discarded/frozen tab
def fmt(s): return f"{s // 60}:{s % 60:02d}"
def name(t): return t["title"].replace("🐴 ", "").removesuffix(" - YouTube")

def rank(t):
    u = t["url"]
    return active.index(u) if u in active else len(active)
tabs.sort(key=rank)
shown = [t for t in tabs if rank(t) < len(active)]  # tabs on screen; background ones may be frozen (slow to probe)

if action == "status":
    for t in tabs:
        s = state(t)
        print(f"{'unavailable' if not s else 'paused ' if s[0] else 'PLAYING'} {fmt(s[1]) if s else ''}  {name(t)}")
    raise SystemExit(0)

if action in ("pause", "toggle"):
    playing = [t for t in (shown or tabs) if (s := state(t)) and not s[0]]
    for t in playing:
        switch_tab(t["targetId"]); js("document.querySelector('video').pause()")
        print("paused:", name(t))
    if playing or action == "pause":
        if not playing: print("nothing playing in a visible tab")
        raise SystemExit(0)

target = next((t for t in tabs if state(t)), None)
if not target:
    print("no YouTube tab responded"); raise SystemExit(1)
js("document.querySelector('video').play()")
import time; time.sleep(1)
s = js(STATE)
print(("playing:" if not s[0] else "FAILED to play:"), name(target), "at", fmt(s[1]))
PY
