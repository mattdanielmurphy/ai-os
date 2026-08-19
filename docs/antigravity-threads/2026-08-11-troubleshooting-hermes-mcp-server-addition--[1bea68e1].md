---
title: "Troubleshooting Hermes MCP Server Addition"
date: "2026-08-11"
conversation_id: "1bea68e192f78abb"
source: "antigravity"
---

# Troubleshooting Hermes MCP Server Addition

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-11 15:14 MDT-6] [context to this point is 0] just trying to get an mcp server added to hermes... can you help me out, because deepseek is fucking up rn

---

## Assistant

The agent got stuck in a loop between port/process conflicts and conflicting Hermes configuration state. Here is how to clean it up and register Proxima cleanly:

Step 1: Kill Orphaned Proxima Processes

The test failed because previous instances of Proxima are running in the background and holding onto port `19222`.

Run this in your terminal to kill any background Proxima instances:

Bash

```
pkill -f "node.*Proxima" || pkill -f "proxima"

```


Verify port `19222` is freed up:

Bash

```
lsof -i :19222

```


*(If anything shows up, kill its PID with `kill -9 <PID>`)*.

Step 2: Remove the Corrupted Hermes MCP Entry

Because the agent manually touched `config.yaml` / `hermes config set`, `hermes mcp add` thinks the server already exists. Clear it out first:

Bash

```
hermes mcp remove proxima

```

Step 3: Re-add the Proxima MCP Server

Run `hermes mcp add` pointing directly to `bun` or `node` and the entrypoint script in your project directory:

Bash

```
hermes mcp add proxima \
  --command ~/.local/bin/node \
  --args /Users/matt/projects/external/Proxima/src/mcp/index.js

```


*(If running under Bun, swap `~/.local/bin/node` for `~/.bun/bin/bun` or `$(which bun)`)*.

Step 4: Test and Reload

Verify the connection and reload the active session:

Bash

```
hermes mcp test proxima

```


Once it passes, reload the MCP directory in your active chat session:

Plaintext

```
/reload-mcp

```

---

## User

[2026-08-11 15:15 MDT-6] [context to this point is 427] but don't I have to run Proxima? It's running right now, but it needs to be

---

## Assistant

Yes! If Proxima **must** be actively running in the background (because it operates as a persistent daemon/service rather than a pure standalone CLI tool), stdio transport creates a fundamental conflict when launched this way.

Here is what's happening under the hood and how to fix it:

The Problem

When Hermes uses **stdio** transport, Hermes **spawns its own new process** of Proxima.

If Proxima's code hardcodes binding to port `19222` on boot—regardless of whether it's launched as a daemon or via an MCP entrypoint—the second instance spawned by Hermes crashes instantly because the main Proxima app is already occupying port `19222`.

Solution 1: Use SSE / HTTP Transport (Recommended if Proxima supports it)

If Proxima runs an HTTP/SSE server alongside its core process, you should point Hermes to that existing process over HTTP instead of having Hermes try to spawn a duplicate process over `stdio`.

Remove the old stdio entry:

Bash

```
hermes mcp remove proxima

```


Add it using SSE URL (adjust port/path if Proxima's MCP SSE endpoint differs):

Bash

```
hermes mcp add proxima http://localhost:19222/mcp

```

Solution 2: Prevent the MCP Entrypoint from Binging Port 19222

If Proxima's MCP interface *must* run via `stdio`, `src/mcp/index.js` should **only** handle stdio IPC communication and **not** attempt to spin up the HTTP/WebSocket server on port `19222` (or it should gracefully ignore `EADDRINUSE`).

In `src/mcp/index.js` (or wherever server initialization happens):

Ensure the MCP entrypoint skips calling `.listen(19222)` if it's meant to communicate strictly over `process.stdin`/`process.stdout`.

Or wrap the server listener in an error handler so `EADDRINUSE` doesn't crash the stdio process:

JavaScript

```
server.listen(19222).on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error('Proxima main app already running on 19222, continuing stdio bridge...');
  }
});

```


Once `src/mcp/index.js` doesn't crash on port conflict, your original `hermes mcp add proxima ...` command will work while the main Proxima process is running.

---

## User

[2026-08-11 15:15 MDT-6] [context to this point is 1065]




[Attached Context: Terminal & CLI Context]

```text

[Terminal & Local Execution Context]

Shell: Zsh on macOS (/bin/zsh)

Local Command Executor Service: http://127.0.0.1:3033/run-command

Headers: x-gemini-thread-saver-key (requires secret configuration)

Inline Terminal Sessions: tmux background sessions monitored via HTTP

```

this is the prompt from the github:




Add the Proxima MCP server to this application’s MCP configuration.




Proxima is a Multi-AI MCP server that connects ChatGPT, Claude, Gemini & Perplexity with local server.




Here is the MCP configuration to add:




{

  "mcpServers": {

    "proxima": {

      "command": "node",

      "args": [

        "/Users/matt/projects/external/Proxima/src/mcp/index.js"

      ]

    }

  }

}







Confirm when done

---

## Assistant

That JSON snippet clarifies the exact setup required by Proxima. Because Proxima runs as a persistent app, its `src/mcp/index.js` script acts as a lightweight **stdio bridge** meant to talk to the running Proxima instance.

The failure happened because DeepSeek got mixed up with process states and tried editing files directly instead of using Hermes's built-in MCP CLI.

Here is how to register it correctly using the exact parameters from the prompt:

Step 1: Clear the corrupted configuration

Since DeepSeek touched the config manually and left Hermes in an inconsistent state:

Bash

```
hermes mcp remove proxima

```

Step 2: Add Proxima via `hermes mcp add`

Run the CLI command using `node` and the path from the README:

Bash

```
hermes mcp add proxima \
  --command node \
  --args /Users/matt/projects/external/Proxima/src/mcp/index.js

```


*(Note: If `node` isn't found in Hermes's subshell environment, supply the full path `~/.local/bin/node` as the `--command` instead).*

Step 3: Verify the connection

While Proxima is running in the background, test the bridge:

Bash

```
hermes mcp test proxima

```


Once `hermes mcp test proxima` returns success, you're all set! Inside your active Hermes session, run `/reload-mcp` to register the new tools.

---

## User

[2026-08-11 15:17 MDT-6] [context to this point is 1443] ok, there's 40 tools it has and I don't think I'm gonna use most of them.

https://github.com/Zen4-bit/Proxima/

should I worry about there being extra tools?

I'm basically going to tell the agent: use THIS one specifically

---

## Assistant

You don't need to worry about the extra tools. Having 40 tools registered in an MCP server won't break anything, but there are a few practical details to keep in mind:

1. Context Window overhead

When an LLM connects to an MCP server, all tool schemas (tool names, descriptions, and argument JSON schemas) are injected into the model's system prompt or tool definition space. With 40 tools, this consumes a chunk of tokens before you even type a message. For capable models like Hermes / Claude / DeepSeek, that extra overhead is negligible, but it's worth knowing where those extra tokens are going.

2. Instructing the Agent

Your plan to tell the agent *"Use THIS tool specifically"* will work smoothly. Large language models easily filter through available tools and target the one requested in the system prompt or message instruction.

3. Filtering Tools (If you ever want to prune them)

If you notice the agent getting confused or want to trim down context overhead, Hermes and the standard MCP protocol allow you to restrict which tools are exposed or enabled. However, if you're explicitly calling out the tool you want to run, leaving the default 40 registered causes no issues.

---
