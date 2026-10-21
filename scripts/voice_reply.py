#!/usr/bin/env python3
"""Report back to voice Claude: a short result for a task that came from voice chat.

  voice_reply.py "<task title>" "<one or two sentence result>"

Writes tmp/voice-outbox/<ts>.json. The Mac connector (services/mac-connector) hands it to voice
Claude on its next connector call (every tool result carries new updates, and voice Claude calls
check_updates each reply after it sent a task), so Matt hears it mid-call.
"""
import json
import sys
import time
from pathlib import Path

OUTBOX = Path.home() / "projects" / "ai-os" / "tmp" / "voice-outbox"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__.strip())
        sys.exit(2)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    f = OUTBOX / f"{int(time.time() * 1000)}.json"
    f.write_text(json.dumps({"title": sys.argv[1], "text": " ".join(sys.argv[2:]), "at": time.strftime("%Y-%m-%d %H:%M")}))
    print(f"queued for voice Claude: {f.name}")
