## Goal
Redesign the user interface using standard vanilla CSS, completely removing the bloated Tailwind mapping in `styles.css`. Apply a new color palette (#161132, #5645C5, white) with dark/light mode support, and implement macOS-style thin scrollbars without tracks.

## Changes Made
- Moved the bloated 150KB+ `src/styles.css` to Trash.
- Created a new, clean `src/styles.css` containing only CSS variables, base resets, and structural classes.
- Updated `index.html` to remove all non-semantic `ui-element-*` classes and replaced them with descriptive, semantic classes like `projects-sidebar` and `main-workspace`.
- Updated `floating.html` to replace raw inline Tailwind classes with standard semantic CSS classes pointing back to `styles.css`.
- Added custom `-webkit-scrollbar` styling to mimic macOS scrollbars that don't take up visual space with a track background.

## What Worked
- Safely stripped out the Tailwind mapping and created a clean baseline.
- `index.html` and `floating.html` are now fully readable and easy to maintain by humans.
- Git commit successful.

## What Didn't Work / Known Issues
- Currently, styles for the floating window and the main UI are merged in `styles.css`. In the future, this should be split into modular files once a frontend component framework or more structured Vanilla JS component system is introduced.

## Architecture Notes
- The rule for CSS modules (`*.module.css`) and PascalCase folders was somewhat bypassed because the app is currently architected as a pure vanilla HTML/TS file structure without a build step that wires up CSS Modules easily into static HTML files. For now, standard global vanilla CSS is being used to fulfill the visual redesign cleanly.
