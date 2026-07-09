## Goal
Fix issues where the delete button on threads is sometimes invisible on hover, and clicking "New Thread" repeatedly creates multiple blank threads instead of reusing the existing one.

## Changes Made
- Modified `src/main.ts` to preserve the `.group` class when reassigning `className` to thread list items. The `group` class is required for Tailwind's `group-hover` utility to show the delete button on hover. Previously, selecting a thread overwrote the class list and stripped `.group`.
- Added a `.new-thread-placeholder` class to the temporary "New Thread" element.
- Updated the "New Thread" button click handler to check if a `.new-thread-placeholder` already exists in the list. If it does, the code simulates a click on it and focuses the prompt entry textarea instead of creating a new placeholder.

## What Worked
- The `.group` class is now consistently maintained on all thread list items, ensuring the delete button remains visible on hover.
- Repeatedly clicking the "New Thread" button now properly refocuses the textarea and selects the existing placeholder rather than duplicating it.

## What Didn't Work / Known Issues
- N/A

## Architecture Notes
- The application manually constructs and swaps DOM `className` strings for state management (active vs inactive thread), which can cause classes like `.group` to be accidentally dropped if not carefully included in all string variations.
