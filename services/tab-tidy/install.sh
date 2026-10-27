#!/bin/bash
# Registers the Tab Tidy helper with Chrome. Run once; safe to re-run.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
ID="epkanaedcolggipgjfpfjjlkmnekdhbb"   # fixed by the "key" in extension/manifest.json
DEST="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts"
mkdir -p "$DEST"
chmod +x "$DIR/host/tab_tidy_host.py"
cat > "$DEST/ca.mattmurphy.tabtidy.json" <<JSON
{
  "name": "ca.mattmurphy.tabtidy",
  "description": "Tab Tidy helper",
  "path": "$DIR/host/tab_tidy_host.py",
  "type": "stdio",
  "allowed_origins": ["chrome-extension://$ID/"]
}
JSON
echo "Helper registered. Now load $DIR/extension in chrome://extensions (Developer mode > Load unpacked)."
