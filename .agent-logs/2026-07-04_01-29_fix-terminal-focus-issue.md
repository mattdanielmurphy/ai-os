## Goal
Fix an issue where the user is frequently unable to type anything into the terminal, requiring an app refresh.

## Changes Made
- Modified `src/main.ts` inside the `document.addEventListener('click', ...)` handler.
- Switched from using `container?.contains(target)` to using `e.composedPath().includes(container)`. 
- **Why**: xterm.js frequently redraws elements (like text nodes and cursor layers) inside the terminal canvas/container. If an element is clicked and then immediately detached/replaced by xterm's rendering engine before the event bubbles up to the `document` level, `e.target` becomes a detached DOM node. As a result, `container.contains(target)` evaluates to `false`. This falsely triggered the fallback condition which called `textarea?.focus()`, stealing focus away from the terminal and placing it into the main prompt input. Because it was consistently stealing focus, the user felt they could never type into the terminal until the app was reloaded. Using `e.composedPath()` ensures we correctly identify clicks that originated within the terminal container, regardless of whether the specific target node was subsequently detached.

## What Worked
- Replaced `contains(target)` with `e.composedPath().includes()` for the main terminal (`container`), `miniContainer`, and `projects-sidebar`.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- `main.ts` uses a global `click` listener on the document to heuristically manage focus between `xterm.js` terminals and the main prompt textarea. 
- Due to the volatility of xterm.js DOM elements, `e.composedPath()` is essential for accurate event delegation here.
