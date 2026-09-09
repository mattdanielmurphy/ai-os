# macOS Environment Reference

## macOS Context & Automation
- Refer to [MAC_ENVIRONMENT.md](file:///Users/matt/projects/ai-os/docs/MAC_ENVIRONMENT.md) before installing software or scripting automation.
- **TCC Permission Reset:** When rebuilding ad-hoc binaries on macOS, run `tccutil reset Accessibility <bundle-id>` and `tccutil reset ListenEvent <bundle-id>` if permission prompts fail.
- **Hammerspoon Reload:** After modifying files in `qwerty-midi-hammerspoon`, run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh`.

## Ground-Truth Visual Verification via Screen Capture
- **Screen Recording & UI Verification**: Antigravity has macOS Screen Recording permissions granted. When debugging native GUI apps (SwiftUI, Hammerspoon webviews, Electron, desktop layouts) or verifying visual rendering, layout scaling, contrast, or typography:
  - NEVER guess visual appearance or assume CSS/Swift code works without checking.
  - Obtain window coordinates using AppleScript System Events (`osascript -e 'tell application "System Events" to tell process "<Name>" to get {position of front window, size of front window}'`).
  - Capture target window using `screencapture -x -R<x,y,w,h> ./tmp/<name>.png`.
  - Inspect with `view_file` to evaluate visual fidelity directly with multimodal vision.

