---
title: "Update Oracle VPS Script"
date: "2026-08-08"
conversation_id: "e586a0bb-e80f-48ed-b882-8dc732988ff9"
source: "antigravity"
---

# Update Oracle VPS Script

## User

Please update the file `/Users/matt/.local/bin/mount-oracle-vps.sh` using `write_to_file` with `Overwrite: true` to the following content:

```bash
#!/bin/bash
set -eo pipefail

MOUNT_DIR="/Users/matt/OracleVPS"
RCLONE_BIN="/opt/homebrew/bin/rclone"
PORT="8765"
WEBDAV_URL="http://127.0.0.1:${PORT}"
LOG_DIR="$HOME/Library/Logs/launch-agents"

mkdir -p "$MOUNT_DIR"
mkdir -p "$LOG_DIR"

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Initializing Oracle VPS mount..."

# Cleanup routine on termination
cleanup() {
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Unmounting $MOUNT_DIR and stopping WebDAV..."
    diskutil unmount force "$MOUNT_DIR" 2>/dev/null || true
    if [ -n "${SERVER_PID:-}" ]; then
        kill -9 "$SERVER_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

# Ensure clean starting state
diskutil unmount force "$MOUNT_DIR" 2>/dev/null || true
killall -9 rclone 2>/dev/null || true
sleep 1

# Start rclone WebDAV server
echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Starting rclone WebDAV backend on ${WEBDAV_URL}..."
"$RCLONE_BIN" serve webdav oracle-vps: \
    --addr "127.0.0.1:${PORT}" \
    --vfs-cache-mode full \
    --vfs-cache-max-age 24h \
    --dir-cache-time 10s \
    --poll-interval 10s &
SERVER_PID=$!

# Wait for WebDAV server to be responsive
for i in $(seq 1 30); do
    if curl -s -o /dev/null "$WEBDAV_URL"; then
        echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] WebDAV server is up. Mounting to $MOUNT_DIR..."
        break
    fi
    sleep 0.5
done

# Mount WebDAV volume into target directory
mount_webdav -v "OracleVPS" "$WEBDAV_URL" "$MOUNT_DIR"
echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Oracle VPS successfully mounted at $MOUNT_DIR."

# Keep process alive tracking the rclone server
wait "$SERVER_PID"
```

---

## Assistant

Created At: 2026-08-08T14:39:20-06:00
Completed At: 2026-08-08T14:39:20-06:00
Created file file:///Users/matt/.local/bin/mount-oracle-vps.sh with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-08T14:39:21-06:00
Completed At: 2026-08-08T14:39:21-06:00
Message sent to "ade49c5a-41d6-4d16-a405-906b44dc8a3a".

The script `/Users/matt/.local/bin/mount-oracle-vps.sh` has been updated with the requested content.

---
