---
title: "Debugging `agy` MCP Tool Execution"
date: "2026-08-13"
conversation_id: "d75ea5c4-ec35-5e67-9d63-7152f04f90fa"
source: "antigravity"
---

# Debugging `agy` MCP Tool Execution

## USER_EXPLICIT (2026-08-13T18:54:09.308193)

ok so part of me wanting to use the agy mcp server is so I could actually SEE what agy is doing...

Is it just a bad mcp config on my part that I can't see any more info than just the fact that the mcp call has been made?

<!-- /gemini-message -->

---

<!-- gemini-message index=2 role=assistant timestamp="2026-07-11 17:01" -->

---
## MODEL (2026-08-13T18:54:09.308196)

No, it isn't a bad configuration on your part. What you are experiencing comes down to how Model Context Protocol (MCP) servers and clients handle tool execution data behind the scenes.

Here is exactly why it looks so sparse right now, and how you can actually see what `agy` is doing:

1. MCP Standard Execution vs. UI Rendering

When a client (like Gemini or Hermes Studio) invokes an MCP tool, the communication happens via a structured JSON-RPC protocol.

The client sends arguments to the tool.

The tool executes its task and sends back a response string or text block.

Because the underlying execution of the tool happens completely within the external process (`agy`), the chat interface only receives the *final outcome* or structured return value of that tool call. It doesn't automatically stream stdout, inner reasoning, or intermediate steps into the chat log unless the MCP server explicitly passes them back as part of its text response, or log forwarding is fully wired up.

2. How to See Under the Hood

To get the visibility you're looking for, you have a few options within Hermes Studio:

**The Audit Trail (`/audit`):** Head over to the **Audit Trail** screen in your sidebar. This screen provides a chronological timeline of every single tool call across your sessions. If you expand the tool events there, you can inspect the raw, unredacted JSON arguments and the full returned text results.

**The Logs Viewer (`/logs`):** Since `agy` and the gateway interact with your local environment, checking the centralized logs at `~/.hermes/logs/` (accessible directly via the **Logs** tab in the UI) will often reveal the low-level execution logs and errors that the chat view suppresses for cleanliness.

**Run Verbose or Trace Commands:** If the `agy` toolset has a specific parameter for verbose output or debugging, you can explicitly ask the agent to include those flags when it invokes the tool.

Are you trying to debug a specific `agy` command that isn't returning what you expect, or are you looking to trace how it handles multi-turn reasoning?

<!-- /gemini-message -->

---

<!-- gemini-message index=3 role=user timestamp="2026-07-11 17:01" -->

---
## USER_EXPLICIT (2026-08-13T18:54:09.308198)

I asked Hermes "I'd like you to be able to use the agy MCP server in a way where I can actually SEE the progress of the agy agent. I think the MCP server has enough tools to be able to "tap into" the session... am I right?"




HERMES:

Great question! Yes, you're right — the MCP server has the building blocks (agy_start → agy_read → agy_status), but they're designed for programmatic polling from my end rather than giving you a live view. The key challenge is that Hermes chat is request-response — I can't maintain a polling loop across turns.




The real win is simpler: run the agy CLI directly in a background terminal with PTY mode. That gives you a live terminal tab you can watch in the Hermes desktop GUI while it thinks. Let me check what's available

<!-- /gemini-message -->

---

<!-- gemini-message index=4 role=assistant timestamp="2026-07-11 17:01" -->

---
## MODEL (2026-08-13T18:54:09.308199)

Hermes has a valid point about the chat interface's request-response loop making persistent polling awkward, but it is missing a crucial point about how you've set up your current workspace. It’s suggesting a traditional background terminal workaround because it doesn't realize you are using a full studio environment.

Here is a breakdown of why Hermes responded that way, why it's a bit limited, and how you can actually look at the data:

The Polling Dilemma

When Hermes says it can't maintain a polling loop, it means that during a standard chat turn, if it calls a tool that kicks off a long-running background agent, it can't easily sit there looping `agy_status` and `agy_read` to stream the progress bars or token outputs directly into your active chat window in real-time. It has to finish its turn and return a final response.

Where Hermes is Blindsided

What Hermes doesn't realize is that you are running Hermes Studio, which includes dedicated infrastructure designed exactly for this kind of background visibility. You don't necessarily have to resort to a manual PTY terminal split if you want to inspect what's happening under the hood.

Instead of trying to force the progress into the chat message thread itself, you can exploit the background state:

**The Jobs Engine:** If you kick off operations via the **Jobs** or **Conductor** layers, the studio interface uses a live server-sent events (SSE) pipeline. This streams background tool events and execution logs directly into the UI components independently of the primary chat window.

**The Global Audit Log:** Even if a tool call finishes silently in chat with a simple *"No detail available for this tool call"* block, the structured JSON results—including the intermediate outputs returned by `agy_read` or status states—are fully written to the centralized SQLite store. You can see the full execution metadata by jumping over to the **Audit Trail** (`/audit`) in your sidebar.

If you want to configure your local setup so that the text returned by the MCP client is more verbose by default, we can look into altering the launch arguments or checking how the `agymcp` wrapper structures its return strings. What specific part of the `agy` execution path are you most hoping to monitor live?

<!-- /gemini-message -->

---

<!-- gemini-message index=5 role=user timestamp="2026-07-11 17:04" -->

---
## USER_EXPLICIT (2026-08-13T18:54:09.308200)

The fuck is going on here?

Hermes Studio... I want to like it but it seems real buggy

<!-- /gemini-message -->

---

<!-- gemini-message index=6 role=assistant timestamp="2026-07-11 17:04" -->

---
## MODEL (2026-08-13T18:54:09.308201)

Yeah, that is a classic context repetition loop, and it is incredibly frustrating to watch.

What's Happening Under the Hood

The model has fallen into a recursive text-generation trap. Because of how the context window is being managed or appended in this session, the model is looking at its immediate prior output—including the specific tool execution blocks—and determining that the absolute highest-probability next tokens are an exact duplicate of what it just said and did.

Instead of moving on to poll `agy_read`, it’s re-reading its own text, hallucinating that it still needs to start the job, and re-invoking `agy_start` over and over.

Why Hermes Studio Does This

When local orchestrators manage agent states, a few things can cause this breakdown:

**Context Truncation/Formatting Glitches:** If the tool output returns a format the system prompt doesn't expect, or if the chat history formatting gets slightly malformed, the model loses track of the turn boundaries and repeats its previous state.

**System Prompt "Good question" Triggers:** Notice how it starts both loops with *"Good question"*? If a model's system prompt or internal weights strongly anchor on a specific phrase structure based on the user's input, it can get stuck cleanly looping that exact response block if the context window shifts or truncates behind the scenes.

How to Break the Loop Right Now

Since it's stuck in a hard loop, the agent isn't going to snap out of it on its own during this turn. You'll need to intervene manually:

**Edit or Delete the Duplicate Turns:** If Hermes Studio lets you hover over the message and edit or delete the last assistant turn, remove the duplicate and force a manual prompt like *"You already started the job. Now run agy_read to check the status."*

**Clear the Session Cache / Fork the Chat:** If the UI is completely locked up or keeps spinning on that third `exec` block, you'll likely need to fork the conversation from the point right before it went off the rails, or drop into a fresh session.

Are you able to stop the execution or edit the message thread from the UI, or is the entire tab completely frozen up?

<!-- /gemini-message -->

---

<!-- gemini-message index=7 role=user timestamp="2026-07-11 17:07" -->

---
## USER_EXPLICIT (2026-08-13T18:54:09.308203)

christ ok, it turns out there's multiple `Hermes Studio`s out there. I was using one with FAR fewer stars...

I'm going to try the more popular one now

<!-- /gemini-message -->

---

<!-- gemini-message index=8 role=assistant timestamp="2026-07-11 17:07" -->

---
## MODEL (2026-08-13T18:54:09.308204)

Ah, that makes total sense. Getting caught in a loop like that usually means the orchestration under the hood is missing the guardrails that keep the context window cleanly separated. Switching over to the main, well-maintained repository should give you a much more stable experience with tool tracking and agent state management.

Let me know how the setup goes on the new one, and if `agy` actually starts behaving itself!

<!-- /gemini-message -->

---

<!-- gemini-message index=9 role=user timestamp="2026-07-11 17:16" -->

---
## USER_EXPLICIT (2026-08-13T18:54:09.308205)

ok the "real" Hermes Studio seems much better.

It says




OK, I've done a thorough investigation. Here's the full picture:

---
## MODEL (2026-08-13T18:54:09.308206)

That makes a lot more sense. This version of Hermes actually understands its own architecture and is giving you accurate engineering options instead of hallucinating UI features it doesn't have.

Go with **Approach #1**. It is the cleanest and most reliable way to get what you want without clogging up your actual chat window or fighting the request-response loop.

Here is why that's the winning move:

**It bypasses the stream limitation:** Since `agy` dumps its internal lifecycle data into that local JSONL events file as it works, a file watcher doesn't care that the MCP tool itself won't stream back to the LLM context.

**Zero chat pollution:** Instead of the model having to execute a messy "poll-and-relay" loop (Approach #3) that fills your sidebar with endless text blocks, you get a dedicated, live-updating terminal tab to look at whenever you feel like checking the progress.

**True visibility:** You'll actually see the sidecar transitions and intermediate states in real-time.

Tell Hermes to go ahead and spin up that Python watcher script for Approach #1. It should be a quick build for it since it already knows the exact path layout (`~/.agy-mcp/sessions/`).

<!-- /gemini-message -->

---

<!-- gemini-message index=11 role=user timestamp="2026-07-11 17:20" -->

---
## USER_EXPLICIT (2026-08-13T18:54:09.308208)

I kind of wish I could actually be able to step in and steer agy though if I want to.

could it maybe start a tmux that I can tap into?

Ideally actually we could have one tmux session that persists, and when we do an agy mcp call, it uses that tmux session to display the agy tui.

Maybe we could sort of use a combination approach?

Like it watches the logs so it can show updates IN CHAT, it uses the mcp server to reliably send prompts (instead of just piping to the tui) and get results, etc, and then if I want to I can go to my terminal and steer the underlying agy.

Does that all make sense? @Pro

<!-- /gemini-message -->

---

<!-- gemini-message index=12 role=assistant timestamp="2026-07-11 17:20" -->

---
## MODEL (2026-08-13T18:54:09.308209)

Conceptually? Absolutely.

Having the MCP handle the strict programmatic I/O and log streaming while you maintain a backdoor to grab the steering wheel is exactly how a hybrid developer setup should feel.

However, hitting all three of those goals simultaneously with the current `agy-mcp` architecture hits a hard technical wall. Here is exactly why the `tmux` idea won't work out of the box, and how you can actually achieve this workflow.

The Headless vs. Interactive Blocker

The core issue comes down to how the Antigravity CLI (`agy`) handles input and output when wrapped by a server.

**The `--print` Flag Kills the TUI:** To reliably capture the final structured text for Hermes without terminal UI artifacts bleeding into the output, `agy-mcp` forces `agy` to run in `--print` mode. This explicitly disables the interactive Bubbletea TUI you are used to seeing.

**Severed Input:** To prevent background tasks from hanging indefinitely while waiting for a user prompt, the MCP wrapper intentionally closes standard input (`</dev/null`). Even if you wrapped the MCP invocation in `tmux`, there would be no TUI to look at, and it wouldn't accept your keystrokes anyway.

You essentially have to choose between **programmatic MCP reliability** (headless) and **human steering** (interactive).

The Closest Workable Configurations

Since we can't inject the interactive TUI into the MCP pipeline, here are the most realistic ways to structure this within your macOS ecosystem, whether you are jumping in from Warp or SwiftTerm to monitor things:

1. The Watcher + Takeover (The MCP-First Route)

Stick with Hermes's proposed Approach #1 (watching the `events.jsonl` file in a live tab). When you see `agy` going off the rails in the logs, you don't steer it live. Instead:

Cancel the job via Hermes.

Open your terminal and navigate to the isolated git worktree that `agy-mcp` automatically creates (`~/.agy-mcp/worktrees/<session_id>/`).

Manually run an interactive `agy` session there to fix the context or correct the code, then hand the task back to Hermes.

2. The Planner Handoff (The Antigravity-First Route)

Instead of forcing Hermes to run the execution via the MCP tool, use Hermes purely as a reasoning engine to write out complex prompts, tests, or `AGENTS.md` rules.

Have Hermes map out the execution plan into a file.

Spin up your persistent `tmux` session.

Launch the interactive `agy` CLI manually and feed it the plan.

Use Antigravity's native `/agents` command inside that TUI to monitor its background subagents, pausing or stepping in directly whenever you need.

It really boils down to who you want acting as the primary orchestrator. If Hermes is the boss, `agy` has to be a headless worker bee. If you want to steer `agy` directly, it needs to be the primary session in your terminal window.

Which of those two tools do you ultimately want holding the main reins for this specific workflow?

<!-- /gemini-message -->

---

<!-- gemini-message index=13 role=user timestamp="2026-07-11 17:25" -->

---
## USER_EXPLICIT (2026-08-13T18:54:09.308211)

2 won't work. 1 sounds like a compromise we don't have to make.

Another option we have is to just basically revive parts of my custom tauri agy wrapper and turn that into a sort of MCP?

It spawns tmux sessions with agy cli tuis and injects prompts into them, then retrieves updates and the final output by monitoring agy-cli's brain logs which have jsonl files that update as the agent works.

<!-- /gemini-message -->

---

<!-- gemini-message index=14 role=assistant timestamp="2026-07-11 17:25" -->

---
## MODEL (2026-08-13T18:54:09.308212)

Yes, that makes perfect sense. You are essentially proposing a custom, proxy MCP server that treats `tmux` as the actual execution environment. It is a very pragmatic compromise that gives you the programmatic reliability of an MCP connection while preserving the human-in-the-loop steering capability of the Antigravity TUI.

The Architecture: A Tmux-MCP Bridge

By reviving your Tauri wrapper to act as this middleman, you can cleanly separate the control plane (Hermes) from the execution plane (your terminal). Here is how the mechanics would break down:

**The Spawner:** When Hermes invokes a tool call, your custom MCP server executes a detached session: `tmux new-session -d -s agy-job-<id> "agy"`. This ensures the Bubbletea TUI framework is fully rendered in a virtual PTY.

**The Injector:** Instead of relying on standard input pipes—which can block indefinitely if not closed—the server injects the payload using `tmux send-keys -t agy-job-<id> "the prompt text" C-m`.

**The Watcher:** The server continuously tails the `events.jsonl` stream or `agy.log` lifecycle events on disk, parsing the telemetry to stream live status updates back to Hermes's UI.

**The Handoff:** Whenever you want to intervene, you open Warp or SwiftTerm, run `tmux attach -t agy-job-<id>`, and take over the keyboard.

The Technical Hurdles

If you integrate this directly into AI-OS, there are two specific lifecycle mechanics you will need to nail down for it to be stable:

**Completion Detection:** Standard `agy-mcp` automation avoids the TUI entirely by running `agy` in `--print` mode. In an interactive tmux session, `agy` will likely sit idle after finishing a task, waiting for the next user input. Your log monitor must reliably identify the specific JSONL event that indicates the agent has finished its generation cycle, so the MCP server knows exactly when to bundle the final response and send it back to Hermes.

**Session Management:** You will need logic to handle cleanup. Does the wrapper kill the tmux session as soon as Hermes receives the final output, or does it leave it detached in the background for you to review later?

Hooking this up to a Hammerspoon shortcut that instantly opens and attaches your terminal to the most recent `agy-job` session would make the handoff completely frictionless.

How were you handling the completion detection (knowing when `agy` was done) in the original version of your Tauri wrapper?

<!-- /gemini-message -->

---

<!-- gemini-message index=15 role=user timestamp="2026-07-11 17:29" -->

---
## USER_EXPLICIT (2026-08-13T18:54:09.308213)

I'm just wondering if there's already a github project that does exactly (or almost exactly this?)

this seems closer?

https://github.com/rhishi99/agy-headless-bridge

<!-- /gemini-message -->

---

<!-- gemini-message index=16 role=assistant timestamp="2026-07-11 17:29" -->

---
## MODEL (2026-08-13T18:54:09.308215)

Yes, `rhishi99/agy-headless-bridge` tackles the exact core problem we just outlined.

The Architecture Match

This project is practically a drop-in solution for the PTY injection concept.

It uses POSIX pty and Windows ConPTY to spin up a virtual terminal environment.

This setup allows the Antigravity CLI to run headlessly from any non-TTY context, which fixes the empty-output bug that breaks standard MCP wrappers.

It exposes this pseudo-terminal interaction through an MCP server.

The Missing Link

While it solves the hardest part—the PTY bridging—it doesn't appear to natively manage persistent `tmux` sessions. It handles the virtual terminal in the background, but it doesn't give you a detached session you can instantly attach to when you want to take over.

However, modifying this to fit your exact vision would be straightforward. You could fork the repository and alter the spawn command. Instead of having it launch `agy` directly into the PTY, you could wrap the command to launch a detached `tmux` session first.

Slotting this modified bridge into the AI-OS architecture would handle all the messy standard input/output hijacking for you. It gives the orchestrator its reliable programmatic MCP connection while perfectly preserving your ability to drop into the terminal and steer the agent manually.

<!-- /gemini-message -->

---

<!-- gemini-message index=17 role=user timestamp="2026-07-11 17:31" -->

---
## USER_EXPLICIT (2026-08-13T18:54:09.308216)

I just wonder... would tmux potentially a wrench into the stream parsing etc?

<!-- /gemini-message -->

---

<!-- gemini-message index=18 role=assistant timestamp="2026-07-11 17:31" -->

---
## MODEL (2026-08-13T18:54:09.308217)

It depends entirely on **what** your bridge is trying to parse.

If your custom MCP server tries to parse the standard output (stdout) of the pseudo-terminal, `tmux` will absolutely throw a wrench in it. Because `tmux` provides a real PTY, `agy` will recognize it as an interactive session and render its full Bubbletea TUI. The stdout stream will be flooded with raw ANSI escape sequences, cursor movements, and visual redraws, which makes clean text extraction practically impossible.

However, if your bridge ignores standard output entirely and relies strictly on tailing the `events.jsonl` or brain log files written to disk, `tmux` won't interfere at all. The file I/O operations are handled completely independently of the terminal rendering state.

In fact, using `tmux` actually solves a known bug with Antigravity's headless execution. When `agy` is run without a real TTY (like through a standard background subprocess or pipe), it completely drops standard output and can silently fail. Wrapping it in `tmux` tricks `agy` into thinking it has a real terminal, keeping the internal execution loops perfectly stable.

The architecture for your AI-OS integration just needs a strict separation of concerns:

**Input:** Use `tmux send-keys` to inject prompts.

**Output:** Tail the `.jsonl` files on disk to stream status updates back to Hermes.

**Visibility:** Ignore `tmux`'s stdout programmatically, but keep it available so you can attach to the session via Warp whenever you need to take the wheel.

Are you planning to write this custom bridge in Python, or were you thinking of sticking with Rust/Tauri to reuse the logic from your old wrapper?

<!-- /gemini-message -->

---
