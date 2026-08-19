---
title: "summarize in detail: 📦 [Bundler] Userscript Bundle Loaded! (Build:..."
date: "2026-08-14"
conversation_id: "f146badd-277e-45d6-b867-c97670d70480"
source: "antigravity"
---

# summarize in detail: 📦 [Bundler] Userscript Bundle Loaded! (Build:...

## User

summarize in detail:
```
📦 [Bundler] Userscript Bundle Loaded! (Build: 1784774860397) (2)
🚀 [Bundler] Executing control-center.js
🚀 [Bundler] Executing d2l-content-tools.user.js
[D2L-DL] Userscript initialized in https://shirtz.cool/products/the-legend-jacket (Top: true)
checking location https://shirtz.cool/products/the-legend-jacket
🔌 [Bundler] M3U8 Stream Capture is disabled via menu settings.
🚀 [Bundler] Executing contentconnections.js
🚀 [Bundler] Executing control-center.js [repeat #2]
[Userscript] ContentConnections Practice Enhancements loaded! 3:13pm thu
[Userscript] Target slide from URL: none
🚀 [Bundler] Executing d2l-content-tools.user.js [repeat #2]
[Userscript] Keydown listener injected into: https://shirtz.cool/products/the-legend-jacket
[Userscript] [syncSlideState] Still searching for slide indicator...
[D2L-DL] Userscript initialized in https://shirtz.cool/web-pixels@0b92dcedw658847c9p94194e39m8bc44e9f/custom/web-pixel-shopify-custom-pixel@0501/sandbox/modern/products/the-legend-jacket (Top: false)
🔌 [Bundler] M3U8 Stream Capture is disabled via menu settin... [repeat #2]
checking location https://shirtz.cool/web-pixels@0b92dcedw658847c9p94194e39m8bc44e9f/custom/web-pixel-shopify-custom-pixel@0501/sandbox/modern/products/the-legend-jacket
🚀 [Bundler] Executing custom-youtube-iframe-fullscreen.js
(anonymous) @ userscript.html?name=Local-Userscript-Dynamic-Loader.user.js&id=f65e81f6-58d8-489e-9958-22e7daba99a5:15105: Allow attribute will take precedence over 'allowfullscreen'.
🚀 [Bundler] Executing apple-music-embedded-player.user.js
iframe loaded
🚀 [Bundler] Executing contentconnections.js [repeat #2]
[Userscript] ContentConnections Practice Enhancements loaded... [repeat #2]
at Object.get (<anonymous>:99:88): ❌ [Bundler] Error in Runtime Error: Failed to read the 'localStorage' property from 'Window': The document is sandboxed and lacks the 'allow-same-origin' flag. SecurityError: Failed to read the 'localStorage' property from 'Window': The document is sandboxed and lacks the 'allow-same-origin' flag.
at Object.get (<anonymous>:99:88): Uncaught SecurityError: Failed to read the 'localStorage' property from 'Window': The document is sandboxed and lacks the 'allow-same-origin' flag.
🚀 [Bundler] Executing custom-youtube-iframe-fullscreen.js [repeat #2]
🚀 [Bundler] Executing apple-music-embedded-player.user.js [repeat #2]
iframe loaded [repeat #2]
[Userscript] Keydown listener injected into: about:blank
checking if player loaded...
[Userscript] Modifier Keydown: code=MetaLeft, alt=false, meta=true, ctrl=false, key=Meta
[Userscript] Modifier Keydown: code=AltLeft, alt=true, meta=true, ctrl=false, key=Alt
checking if player loaded... [repeat #2]
[Userscript] Modifier Keydown: code=KeyI, alt=true, meta=true, ctrl=false, key=Dead
[Userscript] Keydown listener injected into: about:blank [repeat #2] (2)
checking if player loaded... [repeat #3] (36)
[Userscript] [syncSlideState] Still searching for slide indi... [repeat #2]
checking if player loaded... [repeat #4] (40)
[Userscript] [syncSlideState] Still searching for slide indi... [repeat #3]
checking if player loaded... [repeat #5] (24)
```

---

## Assistant

## Perplexity — 02:00 PM

The log shows your **userscript bundler successfully loading and injecting multiple scripts**, but it is doing so on a Shopify product page—and inside several embedded/sandboxed frames where some scripts are not applicable.

Main page activity

The top-level page is:

`https://shirtz.cool/products/the-legend-jacket`

The bundler loads successfully, build 
1784774860397
1784774860397, then executes these scripts:

`control-center.js`

`d2l-content-tools.user.js`

`contentconnections.js`

`custom-youtube-iframe-fullscreen.js`

`apple-music-embedded-player.user.js`

A few messages indicate intended configuration or normal initialization:

M3U8 capture is explicitly disabled in the menu settings.

The ContentConnections enhancement starts, but finds no slide target in the URL.

`d2l-content-tools` injects a keydown listener.

The Apple Music embedded-player script sees an iframe load.

The YouTube fullscreen script emits a browser warning about conflicting iframe permissions.

Why D2L / ContentConnections messages appear

Scripts such as `d2l-content-tools.user.js` and `contentconnections.js` seem designed for D2L course content or slide-based ContentConnections pages. However, they are being run on the unrelated Shirtz Shopify page.

That causes harmless but unnecessary polling:

`[syncSlideState] Still searching for slide indicator...`

`checking if player loaded...`

Those scripts are repeatedly looking for D2L slide controls or a compatible player that do not exist on this product page. The high repeat counts—such as 
36
36, 
40
40, and 
24
24—show their timers are continuing to run.

Frame execution

The scripts also execute in non-top-level documents:

**A Shopify custom-pixel sandbox iframe**

URL begins with `shirtz.cool/web-pixels...`

Logged as `Top: false`

This is a sandboxed environment used for Shopify tracking/custom pixel code.

**`about:blank` iframe(s)**

Your keydown listener injects there too.

This is common when pages dynamically create iframes or embedded widgets.

The `[repeat #2]` messages mostly mean the bundler has executed scripts again in another frame/document context, not necessarily that the same script malfunctioned in one exact page context.

Important error

The meaningful error is:

Failed to read the `localStorage` property from `Window`: The document is sandboxed and lacks the `allow-same-origin` flag.

This occurs in the Shopify custom-pixel sandbox iframe. A sandboxed iframe without `allow-same-origin` cannot access `window.localStorage`, by browser design.

So one of your bundled scripts—or the bundler’s shared configuration/state mechanism—is attempting to access `localStorage` in every frame. That works in the top page, but fails in the pixel sandbox.

The error is not a Shopify page failure; it is a compatibility issue in the userscript loader/script runtime when it runs inside restricted frames.

Other notable messages

`Allow attribute will take precedence over 'allowfullscreen'.`

A browser warning from the YouTube iframe script or page markup.

Modern iframe configuration uses the `allow` attribute for permissions; `allowfullscreen` is redundant. This is not critical.

Modifier key logging:

`MetaLeft`, `AltLeft`, then `KeyI`

You pressed 
Cmd
+
Option
+
I
Cmd+Option+I on macOS, typically the DevTools shortcut.

`key=Dead` can occur with macOS keyboard layouts when Option modifies a key into a dead-key input state. The listener is working as designed.

Overall diagnosis

Nothing indicates that Shirtz itself is broken. Instead:

Your **dynamic userscript loader runs broadly across the top page and iframes**.

Several scripts meant for D2L, ContentConnections, video players, or music embeds run on an unrelated Shopify page.

Those scripts create unnecessary repeated checks.

At least one code path assumes `localStorage` exists, which fails in sandboxed Shopify pixel frames.

Recommended fixes

Restrict each userscript with tighter `@match` / `@include` rules, especially the D2L and ContentConnections scripts.

Avoid running most scripts in iframes unless needed; use `@noframes` for top-page-only scripts.

Guard storage access, for example:


```
js
function canUseLocalStorage() {
  try {
    const storage = window.localStorage;
    const key = "__storage_test__";
    storage.setItem(key, "1");
    storage.removeItem(key);
    return true;
  } catch {
    return false;
  }
}
```


Make polling conditional and bounded: only start

---
