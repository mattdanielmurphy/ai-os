---
title: "Update Oracle VPS Mount Script"
date: "2026-08-08"
conversation_id: "0263316d-2962-464d-87c7-60b0ab4f746e"
source: "antigravity"
---

# Update Oracle VPS Mount Script

## User

Please update `/Users/matt/.local/bin/mount-oracle-vps.sh` using `write_to_file` with `Overwrite: true` to the following content:

```bash
#!/bin/bash
set -eo pipefail

PORT="8765"
WEBDAV_URL="http://127.0.0.1:${PORT}"
LINK_DIR="/Users/matt/Oracle-VPS"
RCLONE_BIN="/opt/homebrew/bin/rclone"
LOG_DIR="$HOME/Library/Logs/launch-agents"

mkdir -p "$LOG_DIR"

cleanup() {
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Unmounting WebDAV volume..."
    diskutil unmount force "/Volumes/127.0.0.1" 2>/dev/null || true
    if [ -n "${SERVER_PID:-}" ]; then
        kill -9 "$SERVER_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

# Ensure clean starting state
diskutil unmount force "/Volumes/127.0.0.1" 2>/dev/null || true
killall -9 rclone 2>/dev/null || true
sleep 1

# Start rclone WebDAV backend
echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Starting rclone WebDAV server on ${WEBDAV_URL}..."
"$RCLONE_BIN" serve webdav oracle-vps: \
    --addr "127.0.0.1:${PORT}" \
    --vfs-cache-mode full \
    --vfs-cache-max-age 24h \
    --dir-cache-time 10s \
    --poll-interval 10s &
SERVER_PID=$!

# Wait for WebDAV server to be up
for i in $(seq 1 30); do
    if curl -s -o /dev/null "$WEBDAV_URL"; then
        echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] WebDAV server is active. Mounting volume..."
        break
    fi
    sleep 0.5
done

# Mount WebDAV volume into /Volumes/127.0.0.1
osascript -e "mount volume \"${WEBDAV_URL}\""
sleep 1

# Create/update clean symlink at ~/Oracle-VPS
rm -f "$LINK_DIR" 2>/dev/null || true
ln -s "/Volumes/127.0.0.1" "$LINK_DIR"

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Successfully mounted Oracle VPS to /Volumes/127.0.0.1 and linked to $LINK_DIR."

# Keep process alive tracking the rclone server
wait "$SERVER_PID"
```

---

## Assistant

Created At: 2026-08-08T14:41:25-06:00
Completed At: 2026-08-08T14:41:25-06:00
Created file file:///Users/matt/.local/bin/mount-oracle-vps.sh with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-08T14:41:26-06:00
Completed At: 2026-08-08T14:41:26-06:00
Message sent to "ade49c5a-41d6-4d16-a405-906b44dc8a3a".

The file `/Users/matt/.local/bin/mount-oracle-vps.sh` has been updated with the requested content.

---
