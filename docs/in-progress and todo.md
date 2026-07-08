## Done
- the threads list for each project should keep loading older ones as you scroll, and never stop
- I want to pretty-print the tool calls

## apparently done
- The tool calls box closes as soon as more output is added, aka while the agent works.
The tool calls box should actually be expanded while the agent works, and only collapse when it's done AND NO LONGER WORKING.
It should start expanded, but have a max-height of 50vh.

## In Progress
- I want to be able to edit a markdown file in vscode and have that add notes to various threads.
	Perhaps when you create a thread, you can add that to the markdown file or something?
	Basically, I'm making all these todos for each project, and I'm copying the prompts back and forth... it'd be easier if there was a way to sync like "thread notes" basically.
	- testing note: it's not working at all. there was no thread notes file, and I want it to be in the PROJECT directory, not my Obsidian notes, although I get why you made that mistake.


This existing version is hard to read:
	```
	{
		"CodeContent": "\"## Goal\\nFix the TUI live stream spinner bug where `\\\\r` and `\\\\b` escape characters were not properly processed, causing the loading string to duplicate in the display. Also fix the appearance of `(B` character set escape sequences.\\n\\n## Changes Made\\n- Modified `src/main.ts` line 1194 to fix the `\\\\r` and `\\\\b` escape characters. In the previous fix, they were mistakenly written as `\\\\\\\\r` and `\\\\\\\\b`, which attempted to match 2-character literal strings against single characters. They are now correctly matching the `\\\\r` and `\\\\b` single characters.\\n- Modified `lastIndexOf` to search for `\\\\n` instead of `\\\\\\\\n`.\\n- Enhanced the regex for stripping ANSI codes (`data.replace(/\\\\x1B(?:\\\\[[0-?]*[ -/]*[@-~]|[\\\\(\\\\)][a-zA-Z0-9])/g, '').replace(/\\\\x1B/g, '')`) so it correctly strips out the `\\\\x1B(B` character set selections, which were previously leaving orphaned `(B` text in the TUI stream.\\n\\n## What Worked\\nProperly interpreting single control characters and correctly stripping non-CSI ANSI escapes successfully restores proper spinner formatting in the plaintext pane without artifacts or duplication.\\n\\n## What Didn't Work / Known Issues\\nThe previous attempt (2026-07-04_16-25) failed because it checked single characters against double-escaped literal strings (`'\\\\\\\\r'` length 2).\\n\\n## Architecture Notes\\nThe terminal PTY output is extremely raw and contains multiple types of ANSI control codes, not just `\\\\x1B[`. It also relies heavily on `\\\\r` without `\\\\n` to draw frame animations.\"",
		"Description": "\"Add log for TUI spinner fix\"",
		"Overwrite": "false",
		"TargetFile": "\"/Users/matthewmurphy/projects/ai-os/.agent-logs/2026-07-04_16-29-tui-live-stream-spinner-fix-2.md\"",
		"toolAction": "\"Writing agent log\"",
		"toolSummary": "\"Write agent log\""
	}
	```

	We should see that markdown block rendered properly, and newlines actually just be newlines as opposed to seeing a bunch of literal `\\n` in the output. So too for `"` instead of `\"`, `\\` instead of `\\\\`, etc.

#### - we have to never use a thread name like "Continuing conversation from history" which is what `agy` apparently picks as the thread name? If the newest thread in the collection of threads that we call ai-os threads

## To do

- new feature idea: have a mode switch above the threads list for a project that controls parallel vs strict queue mode. I want to be able to start a new thread, enter a message, and have it go into a queue, and have the agent only start working on that when all threads before it have finished. So no agents work simultaneously



- I think we should establish a clear nomenclature: ai-os threads: ie, the user-facing threads which, because we run `/clear` all the time just so we can compactify the context for EVERY message, but maintain a thread nonetheless by passing the context off; and then we have agy threads, because technically with running `/clear`, *to agy's perspective* we're creating a new thread all the time... so I mean, they're both "threads" in equal rights, and it feels wrong not to call them anything else. I think maybe I just want it to be documented in this app, in a way where agents operating on this project read this documentation, and they know: "agy thread" is a specific thing and "ai-os thread", or simply "thread" is another
  
- when continuing a thread (auto-clear off), you don't have to inject system instructions into the prompt, because they haven't changed since the start of the thread, and we can assume the the system instructions are already in the thread. We only inject system instructions into brand new threads, aka when auto-clear is enabled.


- rename EVERY instance of: `ts-html-element-\d*` (that's regex syntax) to a reasonable classname.
Obviously you'll change the corresponding css selector if it exists.

- If I type /queue, that should put a message into the queue for THIS thread, running `/clear` first UNLESS the user unchecked it.

- tool calls box STILL auto-folds and fights the user expanding it when they shouldn't be.
  while the agent works, the tool calls box is expanded by default. I don't know how many times I need to say it

- there's still a ton of information missing from the preview window. With ctrl-o mode, you can see all these thoughts; and I'd like to see them in a log on the screen interleaved with the tool calls (if that's hard, separated is fine too)
```
▾ Thought for 2s, 775 tokens
  Prioritizing Tool Usage

  I'm now focusing on tool selection, emphasizing specific tools over general ones where possible. The goal is to optimize efficiency
  by leveraging tools tailored to particular tasks, like viewing files. This strategy promises a more targeted and less error-prone
  approach to problem-solving, which I will continue to refine and implement moving forward.


  Refining Tool Application

  I'm now integrating new rules: avoid `cat` for file operations, favoring `grep_search` and other specialized tools. Before tool
  execution, I'll explicitly list related tools, ensuring the chosen set is optimal. My current focus involves debugging a terminal
  resize issue, examining the `fitAddon.fit()` call to understand the root cause of repeated top lines.


  Investigating Resize Interactions

  I'm now investigating a potential conflict with terminal resizing. It seems calling `term.resize()` manually after `fitAddon.fit()`
  might be redundant, potentially triggering resize events and impacting the terminal's rendering. I'm considering that incorrect
  rows/cols passed to the PTY via `invoke('resize_pty')`, especially within a `tmux` session, could be the root of the garbled output
  observed by the user. I'll examine the calls to `invoke('resize_pty')` more closely for now.
```