# Simplified Sidebar Layout with Inline Threads Implemented

I have refactored the sidebar to simplify the UI, removing the redundant second pane and providing a nested tree structure for threads.

## Key Changes

1. **Merged Sidebar Panes**
   - Removed the separate **Project Threads** header and bottom list container from the HTML.
   - Removed the **list height splitter** (`#sidebar-list-splitter`), allowing the primary projects list to naturally occupy all remaining vertical space in the sidebar.

2. **Inline, Indented Tree Structure**
   - When you click/select a project, it is marked active and is now appended with a slightly indented list of its historical threads directly beneath it.
   - The rest of the projects display below it, scrolling naturally as needed.
   - The inline threads area has a limited height window (`max-h-48`) and displays scrollbars when threads overflow.

3. **Inline Thread Operations**
   - Added a tiny, clean `+` button next to the inline "Threads" label under the active project. Clicking it triggers the standard "Start New Thread" flow, resetting context and starting fresh.

4. **Code Cleanup**
   - Removed obsolete drag resizing events for the old divider.
   - Cleaned up obsolete selectors and styling configurations.
