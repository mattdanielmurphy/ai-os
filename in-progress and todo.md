## In Progress

the tui display has really gone downhill. First of all, often whenever I do collapse or expand, or expand the window, or I run a commnd or something, everything on the terminal screen is liable to disappear completely, and I don't know how to get it back. It seems the screen content comes back when it gets refreshed somehow. Sometimes it gets in a state where I'm unable to paste directly as well. Cmd-clicking links won't open them.

## To do

the reason we added a way to intercept the tui text stream directly was so we could stream the output rather than waiting for the log files to update.
We want to immediately parse and display the part of the text stream that shows the agent steps including the agent thoughts, the tool calls etc.
We're even going to try and stream in plaintext the final output *as it appears*. Once the log file updates, then we'll get the raw markdown and display it properly formatted.



rename EVERY instance of: `ts-html-element-\d*` (that's regex syntax) to a reasonable classname.
Obviously you'll change the corresponding css selector if it exists.