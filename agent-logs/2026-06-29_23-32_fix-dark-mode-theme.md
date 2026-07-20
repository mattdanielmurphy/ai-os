## Goal
Fix the dark mode layout theme colors and prevent sending unsupported `/theme` commands to the `agy` (Antigravity) engine and zsh-based `mini` PTY.

## Changes Made
- Added `darkMode: 'class'` to [tailwind.config.js](file:///Users/matthewmurphy/projects/ai-os/tailwind.config.js) to enable explicit class-based dark mode control.
- Modified [src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts):
  - Implemented `applyTheme()` to dynamically toggle the `dark` class on the root HTML element matching the system theme preferences.
  - Initialized this class on startup.
  - Refactored the `matchMedia` change listener to update the HTML `dark` class and ensure `/theme` commands are ONLY dispatched if the active engine session is running under `claude` (Claude Code). Avoided sending `/theme` to `agy` or the `mini` shell terminal session.

## What Worked
- Project built successfully (`pnpm build`).
- Dark mode theme matches cleanly without sending erroneous `/theme` commands to unsupported engines.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Tailwind CSS dark mode variants require the root element to possess the `dark` class if configured with `darkMode: 'class'`, which gives us explicit deterministic control.
