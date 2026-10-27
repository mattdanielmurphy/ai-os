#!/bin/bash
# Run INSIDE the Testing account right before a LockDown Browser test.
# Lists anything that could make LockDown Browser ask to quit apps.
# Read-only, except --pause-jump / --resume-jump (needs the password):
# Jump Desktop Connect runs as a system service for the whole Mac, so it can
# only be paused for everyone; resume it after the test.
case "${1:-}" in
  --pause-jump)  sudo launchctl bootout system/com.p5sys.jump.connect.service; echo "Jump Desktop Connect paused until --resume-jump or a restart."; exit;;
  --resume-jump) sudo launchctl bootstrap system /Library/LaunchDaemons/com.p5sys.jump.connect.service.plist; echo "Jump Desktop Connect resumed."; exit;;
esac
ok=1
echo "Who is logged in:"
others=$(who | awk '$2=="console"{print $1}' | sort -u | grep -v "^$(id -un)$")
if [ -n "$others" ]; then echo "  WARN: also logged in: $others. Log them out (not just switch) so their apps stop."; ok=0
else echo "  only $(id -un)"; fi

echo "Apps and helpers that LockDown may object to (any user):"
PAT='Jump Desktop|JumpConnect|zoom\.us|ZoomDaemon|Discord|Slack|Teams|Skype|TeamViewer|AnyDesk|Parsec|OBS|Loopback|Audio Hijack|SoundSource|Hammerspoon|Keyboard Maestro|BetterTouchTool|Raycast|Alfred|ChatGPT|Claude|Rectangle|Bartender|Shottr|CleanShot|Docker|UTM|Parallels|VirtualBox|TypeWhisper|Supercharge|rcmd|Screens|VNC'
hits=$(ps -axo user=,comm= | grep -E "$PAT" | grep -v grep | grep -v "^_coreaudiod" | sed -E 's#^([^ ]+) +.*/([^/]+)\.app/.*#\1  \2#' | sort -u)
if [ -n "$hits" ]; then echo "$hits" | sed 's/^/  WARN: /'; ok=0; else echo "  none"; fi

echo "Startup agents skipped for this account:"
launchctl print-disabled "gui/$(id -u)" 2>/dev/null | grep -E '=> (disabled|true)' | sed 's/^/ /'

if [ $ok = 1 ]; then echo "READY: nothing found. Open LockDown Browser from the Dock."
else echo "CHECK the WARN lines above. Root services (Jump Connect) can be paused with: bash $0 --pause-jump"; fi
