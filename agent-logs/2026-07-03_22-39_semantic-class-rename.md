## Goal
Rename the remaining auto-generated `ts-class-*` placeholders in `main.ts` and `styles.css` to proper, human-centric semantic names (e.g. `thread-history-container`, `pause-btn-base`), in order to comply with the project's styling and discoverability architecture rules.

## Changes Made
- `src/main.ts`: Mapped and replaced 16 different `ts-class-*` strings with descriptive semantic CSS class names.
- `src/styles.css`: Replaced the corresponding `ts-class-*` definitions with the new semantic names to maintain style linkage.

## What Worked
Successfully replaced all generic Tailwind translation placeholders (`ts-class-74` through `ts-class-89`) with proper human-readable semantic class names.

## What Didn't Work / Known Issues
None.

## Architecture Notes
The codebase's CSS architecture is now fully aligned with the Semantic CSS rules. Any remaining elements requiring modularization should be split into PascalCase folders moving forward.
