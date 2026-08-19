---
title: "Playwright WebKit Preview Setup"
date: "2026-08-17"
conversation_id: "a6370803-ff9c-40da-af7d-8d01840973a6"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 17, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">Please create the following directory structure and files for the Playwright WebKit live-runner:<br><br>1. Create directory `preview/` and `preview/scripts/`.<br>2. Extract the injected JS and CSS from `Sources/Core/WebViewConfigurationManager.swift` into standalone modular files inside `preview/scripts/`:<br>   - `preview/scripts/suppression.css`: Containing the CSS rules from lines 53-117.<br>   - `preview/scripts/close-interceptor.js`: Containing the JS from lines 147-243.<br>   - `preview/scripts/dynamic-cleaner.js`: Containing the JS from lines 254-333.<br>3. Create `package.json` in the root (`/Users/matt/projects/mindful-browser/package.json`) with Bun / Playwright scripts:<br>```json<br>{<br>  "name": "mindful-browser-preview",<br>  "version": "1.0.0",<br>  "private": true,<br>  "type": "module",<br>  "scripts": {<br>    "preview": "bun run preview/live-runner.ts",<br>    "preview:instagram": "bun run preview/live-runner.ts https://www.instagram.com"<br>  },<br>  "devDependencies": {<br>    "@types/bun": "latest",<br>    "chokidar": "^3.6.0",<br>    "playwright": "^1.49.0"<br>  }<br>}<br>```<br>4. Create `preview/live-runner.ts` which:<br>   - Uses Playwright WebKit (`webkit.launch({ headless: false })`).<br>   - Uses `devices['iPhone 15 Pro']` (or custom 393x852 viewport, DPR 3, touch=true, mobile=true).<br>   - Injects a mock `window.webkit = { messageHandlers: { nativeNavigation: { postMessage: (msg) => console.log('[NativeBridge mock received]', msg) } } }` at document start (`page.addInitScript`).<br>   - Injects all scripts in `preview/scripts/` on `addInitScript` and DOM loaded.<br>   - Uses `chokidar` (or Bun file watcher) to watch `preview/scripts/` and `ExtensionResources/` for file edits.<br>   - On `.css` file edit: hot-replaces the `<style id="mindful-banner-suppression">` tag in the live DOM without full page reload.<br>   - On `.js` file edit: hot-evaluates the script or reloads the page depending on key flag (with immediate feedback in console).<br>   - Accepts CLI url argument (defaulting to `https://www.instagram.com`).<br><br>Write these files surgically and report when complete.</span>



<span title="Responded at 9:27am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The directory structure and files for the Playwright WebKit live-runner have been successfully created.

### Summary of Changes

*   **Directories:** Created `preview/` and `preview/scripts/`.
*   **Modular Scripts:**
    *   [`suppression.css`](file:///Users/matt/projects/mindful-browser/preview/scripts/suppression.css) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/mindful-browser/preview/scripts/suppression.css) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/mindful-browser/preview/scripts/suppression.css): Contains the high-specificity CSS for banner and interstitial suppression.
    *   [`close-interceptor.js`](file:///Users/matt/projects/mindful-browser/preview/scripts/close-interceptor.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/mindful-browser/preview/scripts/close-interceptor.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/mindful-browser/preview/scripts/close-interceptor.js): Contains the logic for intercepting UI navigation/close events.
    *   [`dynamic-cleaner.js`](file:///Users/matt/projects/mindful-browser/preview/scripts/dynamic-cleaner.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/mindful-browser/preview/scripts/dynamic-cleaner.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/mindful-browser/preview/scripts/dynamic-cleaner.js): Contains the DOM observation and cleanup logic.
*   **Configuration:** Added [`package.json`](file:///Users/matt/projects/mindful-browser/package.json) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/mindful-browser/package.json) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/mindful-browser/package.json) with necessary dependencies (`playwright`, `chokidar`, `@types/bun`).
*   **Runner:** Created [`live-runner.ts`](file:///Users/matt/projects/mindful-browser/preview/live-runner.ts) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/mindful-browser/preview/live-runner.ts) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/mindful-browser/preview/live-runner.ts) which configures the WebKit browser (iPhone 15 Pro emulation), injects the native bridge mock, manages scripts, and watches for hot-reloads via `chokidar`.

You can now start the runner with:
`bun run preview` or `bun run preview:instagram`

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota |
| :--- | :--- | :--- | :--- |
| ~40k / ~430k 🟢 (optimal) | 4:25am | 🟢 Clean | 97 ❓, 30 📤 |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/a6370803-ff9c-40da-af7d-8d01840973a6/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>