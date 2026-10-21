#!/bin/zsh
# Install the Mac connector as a launchd agent (always on) and publish it with Tailscale Funnel.
#   ./install.sh            install + start + funnel
#   ./install.sh uninstall  stop, unpublish, move the plist to ~/.Trash
set -e
LABEL=com.matt.agent.mac-connector
PLIST=~/Library/LaunchAgents/$LABEL.plist
DIR=${0:A:h}
LOG=~/Library/Logs/launch-agents/mac-connector.log
if [[ $1 == uninstall ]]; then
  launchctl unload $PLIST 2>/dev/null || true
  /usr/local/bin/tailscale funnel --https=443 off 2>/dev/null || true
  [[ -f $PLIST ]] && mv $PLIST ~/.Trash/
  echo "uninstalled"; exit 0
fi
mkdir -p ${LOG:h}
cat > $PLIST <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>$HOME/.bun/bin/bun</string><string>server.ts</string></array>
  <key>WorkingDirectory</key><string>$DIR</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
PL
launchctl unload $PLIST 2>/dev/null || true
launchctl load $PLIST
/usr/local/bin/tailscale funnel --bg 8777
echo "installed $LABEL; funnel on"
