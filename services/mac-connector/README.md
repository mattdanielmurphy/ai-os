# Mac connector

A remote MCP server so Claude's **voice chat** (claude.ai custom connector) can reach Matt's Mac
in seconds: search notes and past threads (QMD), find / list / read files, and `send_task` to the
Everything project coordinator.

- Runs on `127.0.0.1:8777` (launchd `com.matt.agent.mac-connector`), published by Tailscale Funnel at
  `https://macbook-pro.tail491454.ts.net/mcp/<MAC_CONNECTOR_TOKEN>` on port 443 (claude.ai never reached it on 8443). puma-dev's launchd sockets bind 127.0.0.1 so it doesn't catch Funnel traffic on 443. Every other path is 404.
- Token lives in `~/projects/ai-os/.env`. `bun server.ts --init` creates it if missing and copies the
  full connector URL to the clipboard (it's never printed).
- Read-only. Refuses anything outside `~`, `.env*`, keys, credentials, tokens, `.ssh`, `ai-os/private`.
- `send_task` writes `tmp/voice-task-inbox/queue/*.json` and kicks `scripts/voice_task_inbox.py`, which
  pastes it into the project chat (take-control queue, waits for 60s idle) like the Gmail route.
- Morning check-in: `checkin_today` returns today's talk prompt (`services/checkin/data/checkin-<date>.md`, behind
  `services/checkin/chat_mode.md`) so a regular or voice chat that opens with "Morning check-in" runs it;
  `checkin_record` logs the minutes (ladder) and bullets (vault habit log).
- Install / remove: `./install.sh` / `./install.sh uninstall`. Logs: `~/Library/Logs/launch-agents/mac-connector.log`.
- Add in claude.ai → Settings → Connectors → Add custom connector → paste the URL (no OAuth).
