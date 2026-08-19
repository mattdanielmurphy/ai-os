---
title: "Detecting Chrome DevTools Openness"
date: "2026-08-01"
conversation_id: "b0a86eb4-53f4-4aab-bd1e-504f773a68ae"
source: "antigravity"
---

# Detecting Chrome DevTools Openness

## User

Analyze why DevTools open detection using `outerWidth - innerWidth` or `outerHeight - innerHeight` fails or misfires in Google Chrome userscripts:
1. When DevTools is docked on the right or bottom, `outerWidth` includes browser window borders, title bar, address bar, bookmark bar, and scrollbars. In macOS Chrome (especially high-DPI Retina displays or full-screen spaces), `outerWidth - innerWidth` is often already > 160px even when DevTools is closed!
2. When switching tabs, `innerWidth`/`innerHeight` transiently report 0 or viewport dimensions before layout recalculation, causing false positives on tab switch.
3. Why `console.log("%c", getter)` fails or is suppressed in modern Chrome V8 engines unless DevTools Console tab is specifically active and focused.
4. Recommend a clean, reliable solution for detecting DevTools opening or providing a seamless, non-intrusive access mechanism (e.g. Floating Action Button / quiet trigger badge or reliable DevTools detection pattern).

---

## Assistant

Created At: 2026-08-01T17:15:11-06:00
Completed At: 2026-08-01T17:15:11-06:00
Message sent to "f275218d-32af-4188-b6b1-3de294fb2a33".

I have analyzed the issues with DevTools detection methods and sent a detailed report back to the parent agent outlining why dimensional thresholding and console getters fail in modern Chrome, along with recommended solutions like UI triggers or FABs instead of brittle programmatic detection. I will now end my turn.

---
