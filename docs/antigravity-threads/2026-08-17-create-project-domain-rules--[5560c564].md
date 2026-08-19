---
title: "Create Project Domain Rules"
date: "2026-08-17"
conversation_id: "5560c564-9820-4749-956d-f90df1977a65"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 17, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">Create and write domain rule files in `/Users/matt/projects/ai-os/.rules/`:<br><br>1. File: `/Users/matt/projects/ai-os/.rules/ui_web.md`<br>Content:<br>```markdown<br># Web Application & UI Architecture Rules<br><br>- **Strict Span-Only Styling Invariant**: For `thread.md`, conversation artifacts, and custom markdown layouts, agents MUST use `<span>` tags exclusively (with `display: block;`, `white-space: pre-wrap;`, and inline CSS) for all layout and styling containers. NEVER use `<div>`, `<p>`, or other block HTML tags. Use `<br>` or `<br><br>` tags within `<span>` to preserve line breaks and paragraph spacing without breaking out of the inline span container.<br>- **Architectural Preservation**: When debugging or refactoring established custom UI layouts, CSS modules, or templates, agents MUST isolate the exact root cause while strictly preserving existing styling and DOM structures. No unilateral style simplification.<br>- **Technology Stack**: Use HTML for structure, Javascript/Typescript for logic, and Vanilla CSS or CSS Modules for maximum control. Avoid TailwindCSS unless explicitly requested.<br>```<br><br>2. File: `/Users/matt/projects/ai-os/.rules/hammerspoon.md`<br>Content:<br>```markdown<br># Hammerspoon & macOS Window Automation Rules<br><br>- **Post-Edit Reload Protocol**: Whenever you modify any source/Lua file in `qwerty-midi-hammerspoon` (or projects using Hammerspoon bundles), you MUST immediately run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh` as a mandatory post-flight step before concluding your turn.<br>- **AXUIElement Traversal & Liveness**: In Electron/Chromium AX trees, do not rely on raw stale object references across re-renders. Use structural path replay and validate liveness before dispatching AXPress actions.<br>- **Hammerspoon Webview Focus & IPC**: When debugging `hs.webview` focus and IPC, preserve WKWebView window levels and coordinate-based event taps carefully.<br>```<br><br>3. File: `/Users/matt/projects/ai-os/.rules/audio.md`<br>Content:<br>```markdown<br># Audio & Web Audio API Rules<br><br>- **Web Audio Node Lifetime**: Oscillator and filter nodes should be created once at `initAudioContext()` and modulated via parameter automation (`frequency.linearRampToValueAtTime`, `gain.exponentialRampToValueAtTime`).<br>- **Decay Floor**: Exponential ramps must target a non-zero floor value (e.g. `0.001`) to avoid WebAudio arithmetic errors.<br>- **Feedback Delay Networks**: Maintain sub-unity feedback across staggered delay lines to produce stable diffuse tails without clipping.<br>```<br><br>4. File: `/Users/matt/projects/ai-os/.rules/ios.md`<br>Content:<br>```markdown<br># iOS & Apple Ecosystem Rules<br><br>- **Xcode Project Setup**: Safely modify Xcode projects (`.pbxproj`) to add Swift packages and link dependencies cleanly.<br>- **Apple Reminders & Memo CLI**: Route personal tasks to Apple Reminders via `apple-reminders` CLI with due dates and tags.<br>```<br><br>5. Also update `/Users/matt/projects/ai-os/config/rules_config.json`:<br>Change line 76: `"value": "grok"` to `"value": "gemini"`, and add `"gemini"` to options if not present.</span>



<span title="Responded at 9:50am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested rule files have been created in `/Users/matt/projects/ai-os/.rules/` and the configuration has been updated.

- **Created files:**
    - [`ui_web.md`](file:///Users/matt/projects/ai-os/.rules/ui_web.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/ui_web.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/ui_web.md)
    - [`hammerspoon.md`](file:///Users/matt/projects/ai-os/.rules/hammerspoon.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/hammerspoon.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/hammerspoon.md)
    - [`audio.md`](file:///Users/matt/projects/ai-os/.rules/audio.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/audio.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/audio.md)
    - [`ios.md`](file:///Users/matt/projects/ai-os/.rules/ios.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/ios.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/ios.md)
- **Updated file:**
    - [`rules_config.json`](file:///Users/matt/projects/ai-os/config/rules_config.json) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/config/rules_config.json) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/config/rules_config.json): Default high-reasoning model set to `gemini`.

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota |
| :--- | :--- | :--- | :--- |
| ~35k / ~450k 🟢 (optimal) | 4:50am | 🟡 Uncommitted (5) | 95 ❓, 30 📤 |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/5560c564-9820-4749-956d-f90df1977a65/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>
</span>
</span>