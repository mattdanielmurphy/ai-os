# Siri 2.0 Speech Input — Mic/F5 Key vs. System Dictation

Session finding (beltway to the superwhisper push-to-talk setup). The physical mic key labeled
"F5" on Matt's keyboard is NOT an F5 key — it is a HID **Consumer Control** key.

## Evidence (from Karabiner EventViewer)
Pressing the key logs:
```
{ "name": {"consumer_key_code":"dictation"}, "usagePage":" 12 (0x000c)", "usage":" 207 (0x00cf)" }
```
So macOS treats it as **Dictation**, not F5. Disabling Dictation in System Settings did NOT
stop the "Do you want to enable Dictation? press & or Start Dictation" dialog from appearing.

## The fix (Karabiner)
Append this complex modification to `~/.config/karabiner/karabiner.json` so the consumer key is
remapped to a real F5 (which superwhisper's push-to-talk is set to):
```json
{
  "description": "Dictation key (mic/F5) -> F5 for superwhisper push-to-talk",
  "manipulators": [{
    "from": { "consumer_key_code": "dictation", "modifiers": { "optional": ["any"] } },
    "to": [{ "key_code": "f5" }],
    "type": "basic"
  }]
}
```
- Backup first: `cp ~/.config/karabiner/karabiner.json ~/.hermes/backups/$(date +%Y%m%d_%H%M%S)/`
- Karabiner auto-reloads on save. Don't run `Karabiner-Elements --version` / `--select-profile`
  (launches GUI / hangs). Verify via `log show --last 3m --predicate 'process CONTAINS "Karabiner"'`.

## If the Dictation dialog still appears after the remap
The OS listener is consuming the consumer key below Karabiner's tap. Fallbacks:
- Disable symbolic hotkeys IDs 36/37 (Dictation) via `com.apple.symbolichotkeys`.
- Use a Hammerspoon `hs.eventtap` with a `CGEvent` filter for the consumer usage (0x0c/0xcf),
  converting it to an F5 key-down/up.

## Full diagnostic reference
The complete plist-format decode (Siri KeyboardShortcutSAE SAE1.0, symbolic hotkey IDs,
`fnState`) lives in the `macos/keyboard-shortcuts` umbrella skill under
`references/siri-dictation-mic-key.md`.
