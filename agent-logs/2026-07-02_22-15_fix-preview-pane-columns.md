## Goal
Fix an issue where the markdown preview pane was rendering messages as side-by-side columns instead of vertically stacked rows.

## Changes Made
- Modified `index.html` to add `flex flex-col` classes to the `#markdown-preview-pane` div. This forces it into a flex-column layout so that all child elements (the messages) stack vertically as expected.

## What Worked
- Explicitly adding `flex-col` ensured the layout engine treats the container as a vertical stack, regardless of the child flex contexts (`w-full flex`).

## What Didn't Work / Known Issues
- N/A

## Architecture Notes
- The children of `#markdown-preview-pane` use `w-full flex` to align the message bubbles left or right (`justify-start` vs `justify-end`). When `#markdown-preview-pane` was not explicitly constrained to `flex-col`, these blocks somehow started displaying as side-by-side columns. Adding `flex flex-col` explicitly enforces a vertical timeline flow.
