## Goal
Remove all leftover Tailwind CSS utility classes from `src/main.ts` template literals to ensure 100% compliance with the new Human-Centric UI Architecture (vanilla CSS only).

## Changes Made
- Created a Python regex script (`clean_all_tailwind.py`) to parse `src/main.ts` and surgically strip out any lingering Tailwind classes (e.g. `text-[9px]`, `flex`, `p-2`) while preserving the semantic `ts-html-element-XX` classes and whitelisted interactive classes (`group`, `open-btn`, etc.).
- Refactored dynamic inline Tailwind interpolations for project list items (lines 1305, 1312) into clean semantic classes (`project-item`, `project-item-active`, `project-item-header`, `project-item-header-active`).
- Appended the corresponding CSS for those new project list classes directly to `src/styles.css` so no styling is lost.

## What Worked
- Safely stripped all 30+ instances of Tailwind syntax from `main.ts` without breaking the dynamic layout bindings or existing CSS mappings.

## What Didn't Work / Known Issues
- None. Tailwind is now fully removed from the component rendering code.

## Architecture Notes
- The previous agent successfully compiled all of the initial Tailwind classes into native CSS within `styles.css` under the `.ts-html-element-XX` selectors. By removing the utility classes from `main.ts`, we now strictly rely on those new semantic hooks, preventing future agents from attempting to edit styles via inline Tailwind.
