## Testing
- [ ] `/` commands in the textarea with autocomplete for commands AND for filepaths. include commands like `/model` and `/clear`

- [ ] Repetitive output text appears after tool calls because it's not handling loading spinner correctly
I am seeing this below the tool calls:
```
Agent is thinking & working...
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── [K─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── esc to cancelGemini 3.1 Pro (Low)○ Ruunni⣾ Runni Runnin● unningnning..⣷ Running...ngg...⣯ Running...⣟ ⡿ Runn⢿ Running..⣻ Running...⣽ Running...⣾ Runn⣷ Running⣯ Running...⣟ Running...⡿ R⢿ Runnin⣻ Running...⣽ Running...⣾ ⣷ Runni⣯ Running...⣟ Running...⡿ ⢿ Runn⣻ Running..⣽ Running...
```

It's an old problem but remains unfixed. I'm sure you see what's happening here; the interface is refreshing to show the loading spinner, and our interface is NOT refreshing, and it's just appending every new version of the text with the spinner icon to itself creating an unreadable mess.

## To Do

- [ ] When I submit a new prompt, it's slow and the text hangs in the textarea instead of instantly disappearing, making it clear something is happening, but right now it just sits there until the new terminal opens, which feels super janky

- [x] Sidebar Project Threads: A new sidebar section for each project displaying "Project Threads" (representing a history of past agent logs/conversations).
  - The context of these threads is pruned (omitting code and large file outputs, leaving only high-level steps/discoveries).
  - Designed to work alongside `/clear` by default, recreating continuity by supplying the agent with a lean historical summary of past threads.
  - Allows the agent to query detailed transcripts or full step logs via dedicated helper functions (e.g. leveraging `agy` transcripts/detailed logs) when more information is needed.
- [ ] File browser and VSCode and markdown editors
- [x] open project in Finder button
- [ ] when I enter shell mode, I see a bunch of these characters:  `1;2c0;276;0c1;2c0;276;0c1;2c0;276;0c1;2c0;276;` in the terminal input, presumably from using cmd-arrow key and stuff from when it's in prompt mode so it's sending escape sequences for cursor movement is my guess
- [ ] Queuing of messages
  - The main hurdle to overcome is that if you naively send a /clear along with the prompt, the `/clear` immediately fires, canceling the current task, and the prompt disappears effectively; it's not even run
  - So what we have to do is just hold our messages in our own queue (with a simple UI to show the queued messages and to cancel/edit them), and we'll have to figure out how to determine when the current task has completed.
- [ ] FIX: tmux is broken now slightly ever since it was changed from the main view to a smaller pane that's collapsed by default
  - 1st of all, the view has to expand when I type `/`
  - 2nd, pasting in is unreliable, can't select anything
  - 3rd the bottom of the terminal is cut off
- [ ] BUG: When I turn auto-clear off, it's supposed to NOT run `/clear`. It'll just continue the agy thread in addition to the AI-OS thread.
- [ ] IDEA: have a CODING mode and a CONVERSATION mode
  - makes a lot of sense to me to split these up because the context and instructions are far different (agent coding logs are irrelevant, and there's more things that are relevant like past conversations, web history, etc)
  - conversation mode will just open a (modified) gemini web instance. we can inject our own context still though. maybe we use a CHEAP helper mode to fetch local file context etc
- [ ] Show a message when we run out of quota (this appears in the TUI as `⚠ Individual quota reached. Please upgrade your subscription to increase your limits. \n Resets in 3h50m27s.`)
- [ ] BUG: Expanded agent tasks auto-collapse as the agent continues to work
- [ ] Help the main smart agent stop doing menial tasks like git commits etc.
  - [ ] For git commits in particular, it should just finish, and when it finishes, we commit everything with a dead simple script that just heavily summarizes what the agent said its task was. In fact, we could ask the agent to provide what it would say as a git commit message, and then our script just commits automatically. This accomplishes two things: a tiny amount of token savings for the big model, and the user will see the response faster instead of having to wait for the git commit each time.
  - [ ] I think another menial task that should be optimized significantly is agent-log searching. We should maybe use a dumb and cheap triage model before sending anything to `agy` that finds relevant context, and maybe rewrites the user's message or formulates it into more of a plan; does basic organization. We'll have to be careful that it doesn't editorialize too much though.
  - [ ] The copy button for the whole response is weird; it should appear on the right side, and there should be a thin outline around the reponse, with space above it between the in-progress subtasks.
  - [ ] add a max-width to the chat and have it aligned in the center
  - [ ] The list of "Edited files" at the top of the preview window has a trailing `"` at the end of each file name. And they should be clickable links and reveal each file in finder.
  - [ ] It seems when there's a good amount of historical context being included, sometimes, instead of getting a "historical context" textbox that's collapsed and another box for the user prompt, we just see a user prompt which has a truncated portion of the historical context. Even when we have an extremely long user prompt, we need to be able to show it all. You can and should truncate the super long user prompt, but it must have an expand button and a copy button to copy the whole thing.
  - [ ] Copy buttons should be fixed to the top of the window (like sticky headers) so you can copy the box from the top OR the bottom etc.
  - [ ] Add "breadcrumbs" showing the starts of each message in the thread

### BUGS
- [ ] A strange amount of top-margin and indent gets added to the first sentence of the user prompt after it's sent.
- cmd-click links in tmux TUIs: **not working!**

## In Progress / Testing
