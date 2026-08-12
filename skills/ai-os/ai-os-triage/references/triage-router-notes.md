# Trial Router — Build/Test Detail (2026-08-11 session)

Session mapping of the ai-os triage system ("Siri 2.0") after Matt asked to wire superwhisper
into it.

## Entry points confirmed
- `~/projects/ai-os/scripts/triage_router.py` — the router (627 lines).
- `~/Documents/raycast/ai-os-triage.sh` — Raycast launcher:
  `@raycast.title ai-os Triage Launcher`, `@raycast.argument1` text, calls
  `python3 ~/projects/ai-os/scripts/triage_router.py "$QUERY"`.
- `~/projects/ai-os/bin/triage` — unrelated; it's a context-saving wrapper for verbose
  terminal commands (compiler log slicing). Do NOT confuse with `triage_router.py`.
- `~/projects/ai-os/bin/triage-launcher.sh` — NEW wrapper built this session for superwhisper.

## triage_router.py decision flow (verified by reading)
1. `try_direct_execution(query)` — fast path, no LLM. Handles `open/launch/start`, URL,
   path, `APP_ALIASES` (28 entries incl. chrome/safari/spotify/discord/cursor/arc/brave),
   `.app` bundle discovery, `killall`/`pkill`, `say`, `run`/`exec`.
2. `tier1_triage(query)` — Gemini flash-lite (`gemini-3.1-flash-lite`) classifies.
3. Route: coding intent → `launch_antigravity_app`; non-coding question →
   `open_gemini_webview_thread` (POST `127.0.0.1:3031/api/prompt`, else launch ai-os.app with
   `~/.ai-os/pending_prompt.txt`); `valve_boilerplate` → print web-UI payload; flags `--cli`
   /`--terminal`/`--agy`/`--claude`/leading `/` → force terminal agy.
4. Tier 2: on crash → `tier2_investigation` → escalate; Claude barred (cost guard), paid
   endpoints (`GLM-5.2 (max)`, `google-premium`) require manual config.

Auth/quota reads `~/.gemini/antigravity-cli/settings.json`, `~/.gemini/oauth_creds.json`.
`get_quota()` throttles to weaker model when gemini-2.5-pro remainingFraction < 0.20.

## triage-launcher.sh (the superwhisper wrapper)
Superwhisper passes the transcript in one of several ways; the wrapper is robust to all three:
1. joins `$@` (args mode) — the primary path,
2. falls back to stdin (`cat` if not a TTY),
3. falls back to macOS clipboard (`osascript -e 'the clipboard as text'`).

It strips a leading trigger phrase (case-insensitive `ai os`, `ai-os`, `aiyos`, `a i o s`,
`dispatch`, `triage`) via sed so the prompt reaching the router is clean. Then
`exec python3 /Users/matt/projects/ai-os/scripts/triage_router.py "$QUERY"`.

### Validation run (all green, exit 0)
- `./bin/triage-launcher.sh "ai os open the calculator"` → trigger stripped → forwarded.
- `./bin/triage-launcher.sh "say triage works"` → fast-path "speaking text".
- `echo "open https://example.org" | ./bin/triage-launcher.sh` → stdin mode, fast-path URL.

## Built-in superwhisper discovery (2.17.0, com.superduper.superwhisper)
- Hold-to-talk (`KeyboardShortcuts_pushToTalk`) = carbonKeyCode **63 = F5**, modifiers 0.
- Toggle recording = same F5. changeMode = key 40 (apostrophe).
- Commands live in app DB, NOT a plaintext file — must be created in the superwhisper
  **Commands** UI. Bundle includes `AppleScriptManager.swift` → native script/AppleScript
  command actions are the intended external hook.
- `superwhisper://` URL scheme exists (`com.superduper.superwhisper`) but no documented CLI
  path to run a scripted command externally with text.
- Config: `~/Library/Application Support/superwhisper/` + `com.superduper.superwhisper.plist`;
  commands are NOT in that plist (only hotkeys/onboarding etc.).
