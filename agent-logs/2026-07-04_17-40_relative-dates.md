## Goal
Update the thread dates in the Cmd-K Action Bar and the sidebar thread list to use relative dates (e.g., "1m ago", "10h ago", "2 days ago") with tooltips that display the full date when hovered (e.g. "Jul 4 at 5:30pm"). Use a two-column format for the sidebar thread list where the title and date are horizontally aligned.

## Changes Made
- Created `src/dateUtils.ts` with `getRelativeDateStr` and `getFullDateStr` to format timestamps properly.
- Updated `src/ActionBar/ActionBar.ts` to utilize the new utilities to render a relative date in the search results and a full date on hover.
- Updated `src/ActionBar/ActionBar.module.css` to add `display: flex; justify-content: space-between` to the `.actionBarResultHeader` class to support horizontal alignment of title and date.
- Updated `src/main.ts` to implement relative dates with tooltips in the `renderProjectThreads` method.
- Restructured the `.thread-header` inner HTML in `main.ts` to contain the thread title on the left and the relative date on the right, fulfilling the narrow two-column layout request.

## What Worked
Verified changes compiled successfully via `tsc --noEmit`.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Extracted generic date logic to `src/dateUtils.ts` to prevent code duplication.
- Maintained CSS Modules constraint in `ActionBar.module.css`.
