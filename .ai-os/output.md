# Resizable Layout Splitters Implemented

I have implemented fully resizable splitters for all major panes in the interface to allow flexible layout allocation.

## Key Enhancements

1. **Sidebar Width Resizing**
   - Added a vertical splitter (`#sidebar-splitter`) on the right edge of the projects sidebar.
   - Dragging it resizes the width of the sidebar (constrained between `150px` and `600px`).

2. **Projects List Height Resizing**
   - Replaced the static `h-1/2` height split on the left sidebar.
   - Added a horizontal splitter (`#sidebar-list-splitter`) between the projects list and the project threads header.
   - Dragging it resizes the projects list height to leave enough room for project threads and vice-versa.

3. **Horizontal Terminal vs. Preview split**
   - Added a vertical splitter (`#main-splitter`) between the terminals wrapper (left) and the output markdown preview wrapper (right).
   - Dragging it dynamically adjusts the width percentage ratio between terminals and preview panels.

4. **PTY Fit Alignment**
   - Resizing layout elements automatically triggers terminal dimension recalculations via `debouncedResizePty` so the interactive terminals dynamically fit the new pane widths/heights without clipping.
