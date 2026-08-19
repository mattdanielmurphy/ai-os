---
title: "WebView Live Editing Options"
date: "2026-08-17"
conversation_id: "621556a6-6dbe-44e5-96ff-27e6faa620a0"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">yeah, we've got to implement this</span>



<span title="Responded at 9:27am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

WebKit and Playwright dependencies have finished installing. The live hot-reload environment is ready for use.

### Quick Start:
```bash
bun run preview
```

### What Happens:
- An emulated iPhone 15 Pro WebKit window opens.
- The files inside [`preview/scripts/`](file:///Users/matt/projects/mindful-browser/preview/scripts) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/mindful-browser/preview/scripts) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/mindful-browser/preview/scripts) ([`suppression.css`](file:///Users/matt/projects/mindful-browser/preview/scripts/suppression.css) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/mindful-browser/preview/scripts/suppression.css) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/mindful-browser/preview/scripts/suppression.css), [`close-interceptor.js`](file:///Users/matt/projects/mindful-browser/preview/scripts/close-interceptor.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/mindful-browser/preview/scripts/close-interceptor.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/mindful-browser/preview/scripts/close-interceptor.js), [`dynamic-cleaner.js`](file:///Users/matt/projects/mindful-browser/preview/scripts/dynamic-cleaner.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/mindful-browser/preview/scripts/dynamic-cleaner.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/mindful-browser/preview/scripts/dynamic-cleaner.js)) are injected automatically.
- Any time you save changes to those CSS/JS files in your editor, they are hot-injected into the live WebKit viewport in real time.

Thread reference: [thread.md](file:///Users/matt/.gemini/antigravity/brain/621556a6-6dbe-44e5-96ff-27e6faa620a0/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/621556a6-6dbe-44e5-96ff-27e6faa620a0/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/621556a6-6dbe-44e5-96ff-27e6faa620a0/thread.md)

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">I don't want to have to reload the preview as well, I want it to work on save. Do we need a watcher?<br>And if that's the case, do we need to use playwright?<br>Hmm.. you know what, if it's playwright webkit, that sounds great actually.</span>



<span title="Responded at 9:26am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Yes, Playwright with WebKit is an ideal solution for this workflow. 

### Why Playwright WebKit + Live Watcher Fits Perfectly
1. **Zero manual reloads (True save-and-see)**: A watcher listens to your local JS/CSS files and uses Playwright's WebSocket connection to either re-evaluate the script in-place (hot reload) or trigger a page reload instantly when you hit save in your editor.
2. **Exact Engine & Metrics**: Playwright's WebKit engine renders using Apple's WebKit codebase, and Playwright's device profiles (e.g. `devices['iPhone 15 Pro']`) automatically configure:
   - Exact viewport dimensions (`393 x 852`)
   - Device Scale Factor (`3x` DPR)
   - Mobile touch events (`hasTouch: true`, `isMobile: true`)
   - Safari Mobile User-Agent string

---

### How the Live Preview Runner Works

We can create a lightweight dev runner in your project using **Bun + Playwright WebKit** with two hot-reload modes:

1. **In-Place Hot Injection**: Whenever you save your `.js` or `.css` file, Playwright reads the new code and executes `page.evaluate(...)` into the live DOM instantly—preserving current scroll position and session state without a page refresh.
2. **Full Page Reload on Save (Fallback/Optional)**: For structural initialization scripts (`document-start`), Playwright triggers `page.reload()` immediately on file change.
3. **Mocking Native WebKit Message Handlers**: We can mock `window.webkit.messageHandlers` in the preview environment so your script doesn't crash when attempting to post telemetry/events to Swift.

---

### Recommended Setup

Would you like me to set up a dedicated preview harness (e.g. `preview/live-runner.ts`) in the project? It would:
1. Allow you to point to any target URL (e.g., `https://instagram.com` or local test pages).
2. Auto-watch your script files (`ExtensionResources/content.js` or extracted injected scripts in `Sources/Scripts/`).
3. Launch a standalone emulated iPhone WebKit window side-by-side with your code editor.

Thread reference: [thread.md](file:///Users/matt/.gemini/antigravity/brain/621556a6-6dbe-44e5-96ff-27e6faa620a0/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/621556a6-6dbe-44e5-96ff-27e6faa620a0/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/621556a6-6dbe-44e5-96ff-27e6faa620a0/thread.md)

</span>



</span>

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 17, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">I'd like to be able to edit the javascript injected into the webview and immediately see results without having to build to my iPhone or the simulator because it takes WAY too long to see changes that way.<br>But I'd like to ensure that the view I see is going to look exactly how it will look on the iphone, with the same dimensions and scaling etc.<br>What options do I have?</span>



<span title="Responded at 9:23am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Here are the best, proven options for live-editing and testing injected JavaScript with exact iPhone viewport dimensions, scaling, and WebKit rendering without rebuilding your iOS app:

---

### Option 1: Desktop Safari Responsive Design Mode + Web Inspector (Recommended for Speed & Accuracy)
Since iOS uses **WebKit**, desktop Safari shares the exact rendering engine, viewport scaling rules, and CSS quirks.

1. **Enable Developer Tools in Desktop Safari**:
   - Safari `Settings` $\rightarrow$ `Advanced` $\rightarrow$ Check **Show features for web developers**.
2. **Enter Responsive Design Mode**:
   - Open any target site (e.g. `instagram.com`).
   - Press **`Cmd + Opt + R`** (or `Develop` $\rightarrow$ `Enter Responsive Design Mode`).
   - Select your target iPhone model (e.g., iPhone 15/16 Pro). This forces the exact viewport width, height, device pixel ratio (DPR 3x), and user agent.
3. **Live Injection / Live Reloading**:
   - **Local Userscript Engine**: Run [Tampermonkey](https://www.tampermonkey.net/) or [Userscripts](https://github.com/quoid/userscripts) Safari extension pointing to your local `.js` file via `@require file:///...` or local dev server. Every `Cmd + R` in Safari will instantly re-run the updated JavaScript without touching Xcode.
   - **Live Snippets in Web Inspector**: In Safari Web Inspector (`Cmd + Opt + I` $\rightarrow$ `Sources` $\rightarrow$ `Snippets` or `Console`), run or evaluate your scripts directly in real-time.

---

### Option 2: Live Hot-Reload Local Dev Server into the iOS Simulator (No App Rebuilds)
If you want to test inside the actual `MindfulBrowser` WKWebView wrapper without recompiling Xcode every time you edit JavaScript:

1. **Extract Injected JS into Local Files**:
   - Instead of hardcoding JavaScript strings in `WebViewConfigurationManager.swift`, extract them into distinct `.js` files or serve them from a local HTTP daemon (e.g., `bun --hot serve`).
2. **Development / Debug URL Injection**:
   - In `#if DEBUG` builds, have `WKWebView` load your user scripts from `http://127.0.0.1:port/injected.js` or reload them on page navigation.
3. **Safari Web Inspector Remote Debugging**:
   - Run the simulator **once**.
   - Open Desktop Safari $\rightarrow$ `Develop` $\rightarrow$ `Simulator` $\rightarrow$ `[Your Page]`.
   - You can edit CSS and JS directly in Safari's live DOM/Console or trigger `evaluateJavaScript` on the fly.

---

### Option 3: Headless Playwright / Puppeteer with iPhone Device Emulation + Live Watcher
If you want automated visual verification or side-by-side browser previews:

- Run a small Bun/Node script using **Playwright with WebKit**:
  ```ts
  import { webkit, devices } from 'playwright';
  
  const iPhone = devices['iPhone 15 Pro'];
  const browser = await webkit.launch({ headless: false });
  const context = await browser.newContext({ ...iPhone });
  const page = await context.newPage();
  
  // Inject your local script file automatically on every navigation/reload
  await page.addInitScript({ path: './Sources/Scripts/injected.js' });
  await page.goto('https://instagram.com');
  ```
- Any file watcher (e.g. `bun --watch`) can reload the page whenever you edit your script, giving you sub-second visual feedback in an exact emulated WebKit iPhone frame.

---

### Comparison Matrix

| Approach | Setup Overhead | Engine Fidelity | Reload Speed | Best For |
| :--- | :--- | :--- | :--- | :--- |
| **Safari Responsive Mode** | Zero (Built-in) | Exact WebKit | Instant (`Cmd+R`) | **Fastest iterative UI & JS tuning** |
| **Local Dev Server in WKWebView** | Minimal (One-time setup) | Native iOS WKWebView | Instant on reload | **Testing Swift $\leftrightarrow$ JS bridge & native callbacks** |
| **Playwright WebKit Emulation** | Low (Bun script) | WebKit (Desktop port) | Instant (Watcher) | **Automated visual tests & side-by-side inspection** |

---

### Next Steps & Recommendations
For pure UI styling and DOM manipulation scripts, **Option 1 (Safari Responsive Design Mode with a local userscript / file link)** gives you immediate sub-second feedback. If your script relies heavily on Swift `WKScriptMessageHandler` IPC bridges, **Option 2 (Hot-served local scripts in DEBUG builds)** lets you keep the app running in the simulator while editing JS freely.

Thread reference: [thread.md](file:///Users/matt/.gemini/antigravity/brain/621556a6-6dbe-44e5-96ff-27e6faa620a0/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/621556a6-6dbe-44e5-96ff-27e6faa620a0/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/621556a6-6dbe-44e5-96ff-27e6faa620a0/thread.md)

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota |
| :--- | :--- | :--- | :--- |
| ~45k / ~430k 🟢 (optimal) | 4:25am | 🟢 Clean | 97 ❓, 30 📤 |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/621556a6-6dbe-44e5-96ff-27e6faa620a0/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>