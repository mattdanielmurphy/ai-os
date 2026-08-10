---
title: "la — Launch Agent Manager (CLI Tool)"
name: "la-launch-agent-manager"
description: "la is a CLI tool at ~/.local/bin/la for managing macOS launch agents. Knows all 10 of Matt's custom agents by short name."
category: macos
---

# la — Launch Agent Manager

Matt has a custom CLI tool `la` at `~/.local/bin/la` for managing macOS Launch Agents.

## Available Commands

| Command | Description |
|---------|-------------|
| `la list` | List all agents with status, pid, tmux indicator |
| `la list -k` | Just known agents (skip Apple system noise) |
| `la status <name>` | Detailed view (plist path, mode, pid, state, tmux) |
| `la load <name>...` | Start agent(s) via `launchctl load -w` |
| `la unload <name>...` | Stop agent(s) via `launchctl unload -w` |
| `la restart <name>...` | Unload + load (restart) |
| `la view <name>` | Pretty-print plist as JSON |
| `la logs <name>` | Tail last 50 lines from tmux or log file |
| `la logs -n 200 <name>` | Tail N lines |
| `la edit <name>` | Open plist in default editor |
| `la which <name>` | Print plist path |

## Known Agents

All mapped by short name: `litellm`, `chrome-debug`, `irig-watcher`, `hermes-gateway`, `gemini-ingest`, `userscript-bundler`, `energy-monitor`, `rules-watcher`, `notesync`, `backup-agents`, `agy-proxy`, `turn-swap`, `hermes-webui`, `ai-os-wiki`.

Also fuzzy-matches any other plist by partial label name.

## How it works

- Lists agent status by parsing `launchctl list`
- Shows tmux session status for tmux-wrapped agents (checks with `tmux has-session -t agent-<name>`)
- Captures tmux pane output with `tmux capture-pane` for logs
- Falls back to `~/Library/Logs/launch-agents/` log files