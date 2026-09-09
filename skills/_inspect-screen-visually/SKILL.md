---
name: _inspect-screen-visually
description: "Capture and inspect native macOS application windows or desktop regions using screencapture and view_file for ground-truth visual UI debugging and layout verification."
---

# Visual Screen & Window Inspection (_inspect-screen-visually)

Use this workflow to visually inspect native macOS applications (SwiftUI, AppKit, Hammerspoon webviews, Electron, Qt) when debugging layouts, typography, responsiveness, or visual bugs.

## Workflow

### 1. Locate Application Window Bounds
Use AppleScript System Events to query the front window position and dimensions:

```bash
osascript -e '
tell application "System Events"
    tell process "<AppName>"
        set frontmost to true
        set win to front window
        set winPos to position of win
        set winSize to size of win
        return winPos & winSize
    end tell
end tell
'
```
*(Returns `X, Y, Width, Height`, e.g., `297, 102, 1200, 900`)*

### 2. Capture Window Screenshot to `./tmp`
Capture the target region silently without window shadow using `screencapture -x -R`:

```bash
mkdir -p ./tmp
screencapture -x -R<X>,<Y>,<Width>,<Height> ./tmp/<app_name>_inspect.png
```

*(Alternative for capturing by Window ID without bringing to front: `screencapture -x -l<WindowID> ./tmp/<app_name>_inspect.png`)*

### 3. Check Image Resolution
Verify Retina scaling with `sips`:

```bash
sips -g pixelWidth -g pixelHeight ./tmp/<app_name>_inspect.png
```

### 4. Inspect Visual Output with `view_file`
Call `view_file(AbsolutePath="/Users/matt/projects/.../tmp/<app_name>_inspect.png")` to evaluate visual fidelity, text sharpness, contrast, alignment, and theme styling directly through multimodal vision.
