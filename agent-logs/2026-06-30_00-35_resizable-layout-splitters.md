## Goal
Make all layout panes resizable, particularly addressing the project threads height taking up too much room relative to the projects list.

## Changes Made
- Updated [index.html](file:///Users/matthewmurphy/projects/ai-os/index.html):
  - Removed fixed width constraint on projects sidebar and set dynamic inline style width.
  - Added `#sidebar-splitter` between projects sidebar and main container.
  - Added `#sidebar-list-splitter` between projects list and project threads list headers, replacing static `h-1/2` with inline style height.
  - Replaced the flex split on terminals wrapper and output preview wrapper with `#terminals-wrapper`, `#main-splitter`, and `#preview-wrapper`.
- Updated [src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts):
  - Implemented width drag resizing event handlers for the project sidebar (`#sidebar-splitter`).
  - Implemented height drag resizing event handlers for the projects list (`#sidebar-list-splitter`), allowing custom sharing of space between projects and threads list in the sidebar.
  - Implemented horizontal split resizing handlers between terminals and preview wrappers (`#main-splitter`).
- Updated [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md) and [AG_CONTEXT.md](file:///Users/matthewmurphy/projects/ai-os/AG_CONTEXT.md) to document the resizable layout splitters.

## What Worked
- Successful compilation with TypeScript and Vite (`pnpm build`).
- Splitting layouts cleanly without visual artifacts.
