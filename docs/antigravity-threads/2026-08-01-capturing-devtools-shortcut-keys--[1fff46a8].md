---
title: "Capturing DevTools Shortcut Keys"
date: "2026-08-01"
conversation_id: "1fff46a8-5bd5-41d3-b91e-16b691db3db3"
source: "antigravity"
---

# Capturing DevTools Shortcut Keys

## User

Analyze how to capture Cmd+Option+I (or Cmd+Alt+I) keydown events in Chrome userscripts / Tampermonkey context on macOS:
1. Chrome natively intercepts Cmd+Option+I to toggle Chrome DevTools before standard DOM keydown events fire.
2. How can a userscript piggyback on Cmd+Option+I using window event capturing (`window.addEventListener('keydown', handler, true)` or `document.addEventListener('keydown', handler, { capture: true, passive: true })`) or keyup listening?
3. Provide exact code to trigger `showToast()` when `Cmd+Alt+I` / `Cmd+Option+I` (and `F12` or `Cmd+Alt+J`) is pressed.

---

## Assistant

Created At: 2026-08-01T17:15:48-06:00
Completed At: 2026-08-01T17:15:48-06:00
Message sent to "f275218d-32af-4188-b6b1-3de294fb2a33".

I have analyzed the request and provided the parent agent with the explanation and code to capture `Cmd+Option+I`, `Cmd+Option+J`, and `F12` in a Chrome userscript context. I used `window.addEventListener('keydown', ...)` with `{ capture: true, passive: true }` and explicitly evaluated `e.metaKey`, `e.altKey`, and `e.code === 'KeyI'`.

---
