---
name: "macos-keyboard-shortcuts"
description: "Use when configuring macOS hotkeys, eventtaps, or shortcuts."
category: "macos"
---

# macOS Keyboard Shortcuts & Hotkey Pitfalls

When managing keyboard shortcuts and event taps in automation platforms like Hammerspoon or Karabiner-Elements, pay close attention to global system key capture semantics.

## Eventtaps & Background Reload Focus Guard
- **Never Auto-Enable Key Taps or Windows on Reload:** When reloading background automation or Hammerspoon scripts during development, never auto-start global eventtaps or pop up GUI windows automatically at module import (`init.lua`). Auto-enabling on reload steals focus from the user while they work alongside background agents.
- **Explicit Triggers Only:** Always require explicit manual hotkey press or menu action to start keyboard eventtaps and show controller HUDs.

## Hotkey Traps (`hs.hotkey.bind`)
- `hs.hotkey.bind` registers global Carbon hotkeys at the macOS OS level.
- **System-Wide Capture:** When `hs.hotkey.bind` is active, macOS routes matching keystrokes directly to the binding handler across ALL applications, preventing target applications from receiving the keystroke.
- **Universal Shortcuts Guardrail:** Avoid binding standard macOS application shortcuts like `Cmd+,` (Preferences) globally unless conditionally gated or using non-conflicting modifier combinations (e.g. `Cmd+Alt+,`).
- **Eventtap Alternative:** If a shortcut should only apply when a specific application or modal window is focused, use `hs.eventtap` with window focus checks or pass-through flags (`return false` when non-matching) rather than a global `hs.hotkey.bind`.
