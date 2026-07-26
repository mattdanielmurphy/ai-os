# Conduit — Reference Implementation

**Project:** `~/projects/ai-os/conduit`
**Plan:** `.hermes/plans/2026-07-10_1756-conduit.md`

## Architecture

Dual-window Wails v3 desktop app:
- **Floating HUD** — frameless, always-on-top translucent bar (600x60, expands to 600x400 on response)
- **Hidden Gemini WebView** — loads `https://gemini.google.com`, start hidden, persistent session via `UserDataFolder`

## UI Architecture

- **Mantine v7** + CSS Modules
- Components: `FloatingShell`, `FloatingResponse`, `ThreadSearch`, `SettingsPanel`
- Every component: own directory, `data-ui` attribute, `*.module.css` file
- No Tailwind, no inline styles

## Key Pattern: Hidden Instruction Injection

On submit, Go prepends a system prompt to the user's text before injecting into the Gemini WebView:

```
User types: "what is the capital of France?"
Actually sent: "[system: ...] \n\n what is the capital of France?"
User sees in UI: "what is the capital of France?"
```

Instructions are configurable via `~/.gemini-shell/instructions.txt`.

## IPC Flow

```
FloatingShell keystroke → Go SyncInput() → hidden WebView ExecJS(document.execCommand('insertText'))
Submit → Go SubmitPrompt() → prepend instructions → ExecJS(set content + click send)
Go pollResponse() → ExecJS(read model response) → EmitEvent("response:update") → FloatingShell renders
```

## Related

- `human-centric-ui` skill for the full UI architecture rules
- User's existing userscript (same injection pattern, now in desktop form)