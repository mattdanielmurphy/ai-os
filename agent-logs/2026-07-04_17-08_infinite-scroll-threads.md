## Goal
Implement infinite scroll behavior for the project threads list so it fetches more as the user scrolls down.

## Changes Made
- Modified `src/main.ts` to add a global `maxVisibleThreads` state starting at 15.
- Added a `scroll` event listener to `project-threads-list` which increases `maxVisibleThreads` by 15 when the user reaches the bottom (within 20px).
- Updated `renderProjectThreads` to slice the threads array using `maxVisibleThreads` instead of a hardcoded 5.
- Saved and restored `listEl.scrollTop` in `renderProjectThreads` so the scroll position is maintained when the list re-renders.
- Reset `maxVisibleThreads` to 15 inside `switchToProject` so the new project starts with the default amount of visible threads.

## What Worked
- Tracking state manually and re-triggering `renderProjectThreads` worked correctly. Restoring `scrollTop` is essential because the list container `innerHTML` is cleared during rendering, which otherwise jumps the scroll position to the top.

## What Didn't Work / Known Issues
- It renders everything from scratch on scroll, but since the list size isn't massive and it's just appending simple nodes, performance is adequate.

## Architecture Notes
- The DOM element `#project-threads-list` is maintained in `renderProjectsList` and re-populated dynamically in `renderProjectThreads`. State like scroll event listeners should be attached upon creation in `renderProjectsList`, while dynamic scroll positions must be tracked manually when regenerating inner HTML.
