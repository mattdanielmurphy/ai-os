---
name: uv-claude-wrapper
description: Reference for Astral's uv tool and the local claude-wrapper.py pexpect-based script
metadata:
  type: reference
---

# uv & Claude Wrapper

## What It Is & Why

We use Astral's **[uv](https://docs.astral.sh/uv/)** to bypass Python's modern package management headaches — PEP 668, virtual environments, pipx, and `externally-managed-environment` errors. Python's global package restrictions are a constant annoyance; `uv` eliminates them by running scripts with inline dependency metadata seamlessly, without touching the system Python installation.

## Installation

Installed globally via Homebrew:

```sh
brew install uv
```

No manual PATH configuration needed — Homebrew handles symlinks.

## The Wrapper Tool: `claude-wrapper.py`

A local `claude-wrapper.py` script sits in the project root. It uses `pexpect` to monitor the Claude Code interactive terminal stream and automatically injects a `Ctrl+G` (`\x07`) keystroke, which force-launches the external editor (Antigravity IDE) whenever the Claude agent prompts for text input.

This eliminates the manual step of pressing the hotkey to open the editor.

## How to Use It

Run from the project root:

```sh
uv run ./claude-wrapper.py
```

`uv run` reads the script's inline dependency metadata (PEP 723) and provisions a temporary virtual environment automatically — no manual `venv` setup, no `pip install`, no conflicts with system packages.

## Key Benefits

- **No virtual environment management** — `uv` handles ephemeral environments per-run
- **No `externally-managed-environment` errors** — system Python is never touched
- **No `pipx` overhead** — inline metadata replaces global tool installation
- **Automatic editor launch** — `pexpect` watches the Claude stream and sends the hotkey at the right moment