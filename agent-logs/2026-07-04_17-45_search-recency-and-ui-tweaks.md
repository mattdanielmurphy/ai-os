## Goal
Address user requests to heavily prioritize recency in search results, perfectly align sidebar dates in a vertical column, make the action bar pop up faster, and resume focus to the previous element when the action bar is closed.

## Changes Made
- `src-tauri/src/main.rs`: Refactored `search_project_threads` to use large match scores (e.g. 100_000_000) and added `thread.mtime` to the final score, guaranteeing that newer threads will always appear higher than older threads within the same relevance bracket.
- `src/styles.css`: Added `min-width: 55px` and `text-align: right` to `.thread-date`, and `flex: 1` to `.thread-title` so the dates form a perfect vertical column independent of title length.
- `src/ActionBar/ActionBar.module.css`: Replaced `display: none` with `visibility: hidden` and `opacity: 0` to enable smooth, hardware-accelerated appearance animations, making it feel instantaneous and native.
- `src/ActionBar/ActionBar.ts`: Implemented `previousFocus` cache. When `open()` is called, we store `document.activeElement`, and when `close()` is triggered (via `Esc` or `Enter`), we restore focus to it (e.g., the prompt textarea).

## What Worked
- High-recency sorting integrates elegantly into the existing `score` system.
- Focus resumption provides a highly ergonomic Cmd-K experience.
- The UI alignment fixes address the jagged x-positioning.

## What Didn't Work / Known Issues
- None so far.

## Architecture Notes
- The Action Bar overlay is now constantly in the DOM flow (`display: flex`) but visually hidden to allow proper CSS transition mechanics.
