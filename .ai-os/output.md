# Dark Mode & Theme fixes

I've updated the theme styling controls to properly apply dark mode style rules and resolved the issue where `/theme` commands were sent to the Antigravity engine and zsh terminal.

### What Was Fixed
1. **Root-Level Dark Mode Synchronization**: Tailwind CSS styles prefixed with `dark:` require the `dark` class on the root element to apply when configuring class-based dark mode. I've updated [tailwind.config.js](file:///Users/matthewmurphy/projects/ai-os/tailwind.config.js) to specify `darkMode: 'class'`, and updated [src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts) to dynamically apply/remove the `.dark` class to the HTML element.
2. **Preventing Unsupported `/theme` Commands**: The PTY writing logic previously sent `/theme dark` or `/theme light` commands to the active engine and the mini terminal (zsh). These sessions do not support the `/theme` command. I've restricted these commands to only fire when the active engine is Claude (`claude`).
