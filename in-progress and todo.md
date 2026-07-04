## apparently done
the reason we added a way to intercept the tui text stream directly was so we could stream the output rather than waiting for the log files to update.
We want to immediately parse and display the part of the text stream that shows the agent steps including the agent thoughts, the tool calls etc.
We're even going to try and stream in plaintext the final output *as it appears*. Once the log file updates, then we'll get the raw markdown and display it properly formatted.


## In Progress
Agent tool calls should be displayed like so:
a single box contains all tool calls.
the box expands to take up about 50% of the vertical space available to show various tool calls WHILE THE AGENT IS STILL RUNNING. The box auto-scrolls unless the user scrolls it up manually. If the user scrolls down to the bottom manually, then auto-scroll is re-enabled.
When the agent finishes the task, unless the user is actively interacting with the tool calls box, it should collapse.


## To do
when continuing a thread (auto-clear off), you don't have to inject system instructions into the prompt, because they haven't changed since the start of the thread, and we can assume the the system instructions are already in the thread. We only inject system instructions into brand new threads, aka when auto-clear is enable



rename EVERY instance of: `ts-html-element-\d*` (that's regex syntax) to a reasonable classname.
Obviously you'll change the corresponding css selector if it exists.

