#!/bin/bash
# One-time setup for the clean "Testing" account used for Respondus LockDown Browser.
# Run INSIDE the Testing account (Terminal): bash /Users/Shared/testing-account/setup.sh
#   --dry-run   print what would change, change nothing
#   --undo      re-enable the system-wide agents for Testing
# Matt's own account is never touched: agents are disabled only in Testing's
# launchd domain (gui/<uid>), and prefs are written only to Testing's defaults.
set -u
DRY=0; UNDO=0
for a in "$@"; do case $a in --dry-run) DRY=1;; --undo) UNDO=1;; esac; done
run() { if [ $DRY = 1 ]; then echo "  would run: $*"; else "$@"; fi; }

if [ "$(id -un)" != "testing" ] && [ $DRY = 0 ]; then
  echo "Run this inside the Testing account, not as $(id -un)."; exit 1
fi
UID_T=$(id -u testing)

# System-wide LaunchAgents start for every user. Skip these for Testing only.
# Kept on purpose: Little Snitch agent (without it Little Snitch can't ask about
# LockDown's connections) and arkaudiod (audio routing helper; webcam/mic).
SKIP=(
  com.p5sys.jump.connect.agent          # Jump Desktop Connect (remote access)
  us.zoom.updater                       # Zoom updater
  us.zoom.updater.login.check
  com.Arturia.ArturiaSoftwareCenterAgent
  com.adobe.ARMDCHelper.cc24aef4a1b90ed56a725c38014c95072f92651fb65e1bf9c8e43c37a23d420d
)
echo "1. System-wide startup agents for Testing (uid $UID_T):"
[ $DRY = 0 ] && sudo -v
for l in "${SKIP[@]}"; do
  if [ $UNDO = 1 ]; then run sudo launchctl enable "gui/$UID_T/$l"; echo "  enabled $l"
  else
    run sudo launchctl disable "gui/$UID_T/$l"
    run sudo launchctl bootout "gui/$UID_T/$l" 2>/dev/null
    echo "  skipped for Testing: $l"
  fi
done
[ $UNDO = 1 ] && exit 0

echo "2. Trackpad, keyboard and appearance (copied from Matt's account, Oct 27):"
for d in com.apple.AppleMultitouchTrackpad com.apple.driver.AppleBluetoothMultitouch.trackpad; do
  run defaults write $d Clicking -bool true
  run defaults write $d TrackpadThreeFingerDrag -bool true
  run defaults write $d TrackpadRightClick -bool true
  run defaults write $d TrackpadCornerSecondaryClick -int 0
  run defaults write $d TrackpadTwoFingerDoubleTapGesture -int 1
  run defaults write $d TrackpadTwoFingerFromRightEdgeSwipeGesture -int 3
  run defaults write $d TrackpadThreeFingerHorizSwipeGesture -int 0
  run defaults write $d TrackpadThreeFingerVertSwipeGesture -int 0
  run defaults write $d TrackpadFourFingerHorizSwipeGesture -int 2
  run defaults write $d TrackpadFourFingerVertSwipeGesture -int 2
  run defaults write $d TrackpadFourFingerPinchGesture -int 2
  run defaults write $d TrackpadFiveFingerPinchGesture -int 2
done
run defaults -currentHost write -g com.apple.mouse.tapBehavior -int 1
run defaults write -g com.apple.mouse.tapBehavior -int 1
run defaults write -g com.apple.trackpad.scaling -float 3
run defaults write -g com.apple.mouse.scaling -float 2.5
run defaults write -g com.apple.swipescrolldirection -bool true
run defaults write -g com.apple.trackpad.forceClick -bool true
run defaults write -g KeyRepeat -int 5
run defaults write -g InitialKeyRepeat -int 15
run defaults write -g AppleKeyboardUIMode -int 2
run defaults write -g com.apple.keyboard.fnState -bool false
run defaults write -g AppleInterfaceStyleSwitchesAutomatically -bool true
run defaults write -g AppleLocale -string en_CA

echo "3. Dock: only LockDown Browser and Safari, same size and auto-hide as Matt's:"
tile() { echo "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>$1</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"; }
run defaults write com.apple.dock persistent-apps -array "$(tile '/Applications/LockDown Browser.app')" "$(tile '/Applications/Safari.app')"
run defaults write com.apple.dock persistent-others -array
run defaults write com.apple.dock show-recents -bool false
run defaults write com.apple.dock autohide -bool true
run defaults write com.apple.dock autohide-delay -float 0
run defaults write com.apple.dock tilesize -int 128
run killall Dock

echo "4. Safari homepage: canvas.ualberta.ca"
SAF=~/Library/Containers/com.apple.Safari/Data/Library/Preferences/com.apple.Safari
if [ $DRY = 0 ] && [ ! -d ~/Library/Containers/com.apple.Safari ]; then
  echo "  Safari hasn't been opened in Testing yet. Open Safari once, quit it, then rerun this script."
elif run defaults write "$SAF" HomePage -string "https://canvas.ualberta.ca" 2>/dev/null \
   && run defaults write "$SAF" NewWindowBehavior -int 0 2>/dev/null; then
  echo "  set (check Safari > Settings > General if it didn't stick)"
else
  echo "  macOS blocked writing Safari's settings. Set it by hand:"
  echo "  Safari > Settings > General > Homepage = https://canvas.ualberta.ca"
fi

echo "5. Login items for Testing (should be none):"
osascript -e 'tell application "System Events" to get the name of every login item' 2>&1 | sed 's/^/  /'

echo "Done. Log out of Testing and back in, then run: bash /Users/Shared/testing-account/pretest_check.sh"
