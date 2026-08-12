---
name: ai-os-triage
description: Routes ai-os/Siri-2.0 prompts via triage_router.py.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ai-os, triage, siri, voice, superwhisper, raycast, router, speech]
    related_skills: [ai-os-conversation-logs, agy, macos-keyboard-shortcuts]
---

# AI-OS Prompt Triage Router ("Siri 2.0") & Voice Input

## When to Use
- Matt refers to "Siri 2.0", the triage system, or asks to fire a prompt/command by voice.
- Working on the ai-os prompt routing pipeline at `~/projects/ai-os`.
- Integrating speech-to-text (superwhisper) or a launcher (Raycast) into the triage flow.
- Diagnosing why a spoken/typed prompt went to the wrong destination (fast-path vs Gemini).

The ai-os triage pipeline routes a plain-language query to the cheapest/fastest correct
destination. It is Matt's "Siri 2.0" idea: trivial commands resolve instantly with zero LLM
overhead; anything needing reasoning funnels into a Gemini/ai-os flow.

## Architecture (current)
Entry points:
- **Raycast**: `/Users/matt/Documents/raycast/ai-os-triage.sh` (`@raycast.title ai-os Triage
  Launcher`, one text arg) → calls `python3 ~/projects/ai-os/scripts/triage_router.py "$QUERY"`.
- **Speech (superwhisper)**: `bin/triage-launcher.sh` (see Speech integration below).

`scripts/triage_router.py` decides, in strict order:
1. **Fast-path direct execution** (no LLM, near-instant) via `try_direct_execution()`:
   - `open X` / `launch X` / `start X` → opens URLs, paths, or apps via the `APP_ALIASES`
     map (safari, chrome, spotify, discord, cursor, etc.). Opens raw `.app` bundles under
     `/Applications`/`/System/Applications`/`~/Applications` as a fallback.
   - `killall X` / `pkill X` (process termination).
   - `say X` (macOS text-to-speech).
   - `run X` / `exec X` (arbitrary shell).
   Returns True if it handled the query (and exits), else falls through.
2. **Tier 1 LLM classification** (`tier1_triage`): if not fast-pathed, Gemini flash-lite
   classifies as `simple_non_coding` / `coding_standard` / `coding_complex` /
   `valve_boilerplate`. Model choice honors live Google quota — downgrades to a weaker model
   when 5h quota < 20% (`get_quota()`).
3. **Routing**:
   - Coding/file intent → `launch_antigravity_app()` — GUI-scripts Antigravity.app (new
     conversation, clipboard paste, send).
   - Non-coding question → `open_gemini_webview_thread()` — POST to local ai-os API at
     `127.0.0.1:3031/api/prompt`, else launches ai-os.app with a pending-prompt file.
   - `valve_boilerplate` → prints a "paste this into a web UI" payload to save quota.
   - `--cli`/`--terminal`/`--agy`/`--claude` flags or leading `/` → force terminal `agy`.
4. **Tier 2 escalation**: on crash, re-analyzes the error and retries with a stronger model.
   Claude is barred from autonomous invocation (cost guard).

## Speech integration (superwhisper → triage)
Goal: hold a key (or say a trigger phrase) → superwhisper transcribes → run `triage.py`.

- superwhisper 2.x natively supports **Commands** with a script/AppleScript action
  (the bundle has `AppleScriptManager.swift`). Its command storage is a SQLite/app DB, NOT a
  plaintext file — you cannot pre-create a command from a script; the user must add it once
  in the superwhisper **Commands** UI.
- `bin/triage-launcher.sh` is the wrapper superwhisper should call. It is robust to how the
  transcript arrives: it joins `$@`, falls back to **stdin**, then to the **clipboard**, and
  strips a leading trigger phrase (`ai os`, `ai-os`, `aiyos`, `dispatch`, `triage`) so the
  prompt reaching the router is clean. Exec: `python3 scripts/triage_router.py "$QUERY"`.
- Current superwhisper hotkeys (2.17): hold-to-talk (push-to-talk) = **F5** key 63, no
  modifier. Toggle recording = same. There's a `superwhisper://` URL scheme but no documented
  CLI path to run a scripted command externally — the Command script-action is the hook.

See `references/triage-router-notes.md` for exact build/test detail and known quirks. The
superwhisper wrapper is stored at `scripts/triage-launcher.sh` in this skill — copy it to
`~/projects/ai-os/bin/triage-launcher.sh` to (re)deploy.

## Pitfalls
- **"open the X" misses the fast-path.** `try_direct_execution` matches `open ` literally
  with an intervening space, so `"open the safari"` (with "the") falls through to LLM/route
  instead of opening instantly. Phrase commands without "the": say `"open safari"`, `"open
  music"`. Do NOT extend the router to strip "the" unless asked — surgical fix only.
- **The Antigravity fallback is stale/broken** on Matt's machine: `launch_antigravity_app`
  drives Antigravity.app via osascript keystrokes, which macOS blocks (error 1002, "osascript
  is not allowed to send keystrokes") and Antigravity.app may not even be installed. If a
  non-fast-path query lands there it errors. The working destinations in practice are the
  fast-path and (when fixed) the ai-os Gemini webview / agy terminal routes.
- **Command storage is not plaintext** — never try to reverse-engineer superwhisper's SQLite
  for commands; wire via the UI Commands panel.
- Router reads `~/.gemini/antigravity-cli/settings.json` + `oauth_creds.json`; authless
  fallback returns "normal" quota and a safe default classification.
