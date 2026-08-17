# Hammerspoon & macOS Window Automation Rules

- **Post-Edit Reload Protocol**: Whenever you modify any source/Lua file in `qwerty-midi-hammerspoon` (or projects using Hammerspoon bundles), you MUST immediately run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh` as a mandatory post-flight step before concluding your turn.
- **AXUIElement Traversal & Liveness**: In Electron/Chromium AX trees, do not rely on raw stale object references across re-renders. Use structural path replay and validate liveness before dispatching AXPress actions.
- **Hammerspoon Webview Focus & IPC**: When debugging `hs.webview` focus and IPC, preserve WKWebView window levels and coordinate-based event taps carefully.
