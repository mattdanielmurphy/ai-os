## apparently done

## In Progress
- The tool calls box closes as soon as more output is added, aka while the agent works.
The tool calls box should actually be expanded while the agent works, and only collapse when it's done AND NO LONGER WORKING.
It should start expanded, but have a max-height of 50vh.

- the threads list for each project should keep loading older ones as you scroll, and never stop

- I want to pretty-print the tool calls:
This existing version is hard to read:
```{
  "CodeContent": "\"## Goal\\nFix the TUI live stream spinner bug where `\\\\r` and `\\\\b` escape characters were not properly processed, causing the loading string to duplicate in the display. Also fix the appearance of `(B` character set escape sequences.\\n\\n## Changes Made\\n- Modified `src/main.ts` line 1194 to fix the `\\\\r` and `\\\\b` escape characters. In the previous fix, they were mistakenly written as `\\\\\\\\r` and `\\\\\\\\b`, which attempted to match 2-character literal strings against single characters. They are now correctly matching the `\\\\r` and `\\\\b` single characters.\\n- Modified `lastIndexOf` to search for `\\\\n` instead of `\\\\\\\\n`.\\n- Enhanced the regex for stripping ANSI codes (`data.replace(/\\\\x1B(?:\\\\[[0-?]*[ -/]*[@-~]|[\\\\(\\\\)][a-zA-Z0-9])/g, '').replace(/\\\\x1B/g, '')`) so it correctly strips out the `\\\\x1B(B` character set selections, which were previously leaving orphaned `(B` text in the TUI stream.\\n\\n## What Worked\\nProperly interpreting single control characters and correctly stripping non-CSI ANSI escapes successfully restores proper spinner formatting in the plaintext pane without artifacts or duplication.\\n\\n## What Didn't Work / Known Issues\\nThe previous attempt (2026-07-04_16-25) failed because it checked single characters against double-escaped literal strings (`'\\\\\\\\r'` length 2).\\n\\n## Architecture Notes\\nThe terminal PTY output is extremely raw and contains multiple types of ANSI control codes, not just `\\\\x1B[`. It also relies heavily on `\\\\r` without `\\\\n` to draw frame animations.\"",
  "Description": "\"Add log for TUI spinner fix\"",
  "Overwrite": "false",
  "TargetFile": "\"/Users/matthewmurphy/projects/ai-os/.agent-logs/2026-07-04_16-29-tui-live-stream-spinner-fix-2.md\"",
  "toolAction": "\"Writing agent log\"",
  "toolSummary": "\"Write agent log\""
}```

We should see that markdown block rendered properly, and newlines actually just be newlines as opposed to seeing a bunch of literal `\\n` in the output. So too for `"` instead of `\"`, `\\` instead of `\\\\`, etc.

## To do

- we have to 
- when continuing a thread (auto-clear off), you don't have to inject system instructions into the prompt, because they haven't changed since the start of the thread, and we can assume the the system instructions are already in the thread. We only inject system instructions into brand new threads, aka when auto-clear is enabled.


- rename EVERY instance of: `ts-html-element-\d*` (that's regex syntax) to a reasonable classname.
Obviously you'll change the corresponding css selector if it exists.

