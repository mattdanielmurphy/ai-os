## Goal
Update sidebar UI to better indicate selected thread, disable text selection cursor on threads, constrain project thread list to 50vh with scrolling, and reduce vertical space taken by thread items.

## Changes Made
- `src/styles.css`: 
  - Added `max-height: 50vh; overflow-y: auto;` to `.thread-history-list` to constrain thread lists and allow scrolling.
  - Added `user-select: none;` to thread items to prevent text selection cursor.
  - Reduced padding from `2px 4px` to `1px 4px` on thread items, and reduced gap from `2px` to `0px`.
  - Reduced gap in `.thread-header` from `8px` to `4px`.
  - Enhanced `.thread-history-item.active` style with a stronger background and a primary-colored left border.

## What Worked
All CSS styles were successfully updated. The thread items should now be more compact, text selection disabled, and scrolling constrained.

## What Didn't Work / Known Issues
None.

## Architecture Notes
Thread active states are toggled via JS adding `.active` class to `.thread-history-item` in `src/main.ts`.
