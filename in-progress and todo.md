## apparently done

## In Progress
- The tool calls box closes as soon as more output is added, aka while the agent works.
The tool calls box should actually be expanded while the agent works, and only collapse when it's done AND NO LONGER WORKING.
It should start expanded, but have a max-height of 50vh.

- the threads list for each project should keep loading older ones as you scroll, and never stop

## To do
- when continuing a thread (auto-clear off), you don't have to inject system instructions into the prompt, because they haven't changed since the start of the thread, and we can assume the the system instructions are already in the thread. We only inject system instructions into brand new threads, aka when auto-clear is enabled.


- rename EVERY instance of: `ts-html-element-\d*` (that's regex syntax) to a reasonable classname.
Obviously you'll change the corresponding css selector if it exists.

