[2026-07-04 20:15] User:
how to use litellm claude code to openrouter server with nimbalyst?

---

[2026-07-04 20:15] Assistant:
To route **Claude Code** through **LiteLLM** to **OpenRouter**, and access it visually inside **Nimbalyst**, you need to bridge three layers.

**LiteLLM** acts as the proxy server that translates Anthropic format to OpenRouter format.

**Claude Code** is configured to talk to your local LiteLLM server instead of Anthropic's servers.

**Nimbalyst** loads your repository and interacts natively with your local Claude Code setup.

Here is the step-by-step configuration.

Step 1: Configure and Start LiteLLM

First, you need to point LiteLLM to OpenRouter and define the models Claude Code expects to see.

Create a `config.yaml` file for LiteLLM:

YAML

```
model_list:
  - model_name: claude-opus-4-7
    litellm_params:
      model: openrouter/anthropic/claude-3.5-sonnet # Or any OpenRouter model you prefer
      api_key: os.environ/OPENROUTER_API_KEY
  - model_name: claude-sonnet-4-6
    litellm_params:
      model: openrouter/anthropic/claude-3.5-sonnet
      api_key: os.environ/OPENROUTER_API_KEY
  - model_name: claude-haiku-4-5-20251001
    litellm_params:
      model: openrouter/anthropic/claude-3-haiku
      api_key: os.environ/OPENROUTER_API_KEY

```


Set your environment variables and start the LiteLLM proxy:

Bash

```
export OPENROUTER_API_KEY="your-openrouter-key-here"
export LITELLM_MASTER_KEY="sk-your-chosen-local-key"

litellm --config ./config.yaml

```


*Your proxy will now be running at `http://0.0.0.0:4000`.*

Step 2: Configure Claude Code Global Settings

Claude Code stores its global environment overrides in `~/.claude/settings.json`. By modifying this file, both the terminal CLI and Nimbalyst will respect the redirected endpoint.

Open `~/.claude/settings.json` in a text editor.

Structure the `env` block to route traffic to LiteLLM and bypass the native Anthropic auth:

JSON

```
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://0.0.0.0:4000",
    "ANTHROPIC_AUTH_TOKEN": "sk-your-chosen-local-key",
    "ANTHROPIC_API_KEY": "",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-7",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-6",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-haiku-4-5-20251001"
  }
}

```


*(Setting `"ANTHROPIC_API_KEY": ""` is critical to prevent Claude Code from trying to enforce a native web login).*

Step 3: Connect to Nimbalyst

Nimbalyst uses your system's underlying Claude Code installation via its SDK.

Launch **Nimbalyst**.

Go to **Settings** → **Agent Providers**.

Toggle on **Claude Code**.

Open your project folder in Nimbalyst.

When you open the Agent panel (the right sidebar) or select a Claude model from Nimbalyst's interface, it will spin up the local Claude Code instance. Thanks to your `settings.json`, Claude Code will instantly pass those API calls down through your local LiteLLM proxy right into OpenRouter.

---

[2026-07-04 20:32] User:
ok, I have litellm running. If I launch claude code in my terminal, it successfully sends requests to the litellm server which sends it to openrouter. It works perfectly, so I don't want to change my litellm config.

this is my litellm config:

```

model_list:

- model_name: claude-opus-4-8

litellm_params:

model: openrouter/deepseek/deepseek-v4-flash

max_tokens: 8192 # Protects the generation output window safely




litellm_settings:

drop_params: true

```




But there's nothing in claude's settings.json:

```

cat ~/.claude/settings.json 

{

  "enabledPlugins": {

    "swift-lsp@claude-plugins-official": true,

    "warp@claude-code-warp": true

  },

  "env": {},

  "extraKnownMarketplaces": {

    "claude-code-warp": {

      "source": {

        "repo": "warpdotdev/claude-code-warp",

        "source": "github"

      }

    }

  },

  "hooks": {},

  "permissions": {

    "allow": [],

    "deny": []

  },

  "skipDangerousModePermissionPrompt": true,

  "theme": "auto"

}%                                                                                                                                       

```




BUT if you see the attached screenshot, the setting of the base key IS somewhere. Could it be in my env, and the problem here is this app has it's own separate env vars?

---

[2026-07-04 20:32] Assistant:
Looking at your screenshot, Claude Code is hitting `http://localhost:8082` instead of LiteLLM's standard port `4000`. If it's working flawlessly in your terminal right now with an empty `~/.claude/settings.json`, those settings are **100% coming from your active terminal session environment variables**.

You likely have `ANTHROPIC_BASE_URL=http://localhost:8082` and `ANTHROPIC_API_KEY=...` exported in your `~/.zshrc`, `~/.bashrc`, or a local `direnv` environment.

Why Nimbalyst Isn't Picking It Up

When you launch a GUI macOS application like **Nimbalyst** (whether via the Applications folder, Raycast, or Alfred), it **does not inherit your terminal's shell environment variables**. It runs in a clean desktop session environment.

Because Nimbalyst spins up Claude Code as a background child process, that background process sees a completely blank slate: no `ANTHROPIC_BASE_URL` and no `ANTHROPIC_API_KEY`. It defaults back to native Anthropic settings and fails.

The Fix: Make the Environment Global to Claude Code

To make sure Nimbalyst's background agent runner sees the exact same setup your terminal does, you need to migrate those environment variables into Claude Code’s global configuration file so they load regardless of *how* the process is spawned.

Update your `~/.claude/settings.json` to include your working terminal configuration in the `"env"` block:

JSON

```
{
  "enabledPlugins": {
    "swift-lsp@claude-plugins-official": true,
    "warp@claude-code-warp": true
  },
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:8082",
    "ANTHROPIC_API_KEY": "none"
  },
  "extraKnownMarketplaces": {
    "claude-code-warp": {
      "source": {
        "repo": "warpdotdev/claude-code-warp",
        "source": "github"
      }
    }
  },
  "hooks": {},
  "permissions": {
    "allow": [],
    "deny": []
  },
  "skipDangerousModePermissionPrompt": true,
  "theme": "auto"
}

```

Alternatively: Launch Nimbalyst from the Terminal

If you want a quick way to verify this without changing files yet, you can force Nimbalyst to inherit your terminal's working environment by launching it directly from your command line:

Bash

```
open -a Nimbalyst

```


Once the global `settings.json` is updated, you can fully close and restart Nimbalyst, and the visual app will route through your LiteLLM port seamlessly.

---

[2026-07-04 20:41] User:
can you do subagents in nimbalyst?

---

[2026-07-04 20:41] Assistant:
Yes, you can absolutely use **Claude Code subagents** inside Nimbalyst.

Because Nimbalyst interacts natively with your underlying Claude Code installation, any built-in subagents (`Explore`, `Plan`, etc.) or custom markdown-configured subagents will execute perfectly.

However, there is a distinct conceptual difference in Nimbalyst between **Subagents** and **Parallel Sessions**.

1. Claude Code Subagents (Internal Delegation)

These are workers that live entirely *inside* a single Claude Code session. When you run a task in Nimbalyst, the main Claude Code process can spin up an isolated context window to handle a heavy or noisy task (like reviewing code or parsing documentation) and return only the summary to your main chat.

To define a custom subagent that Nimbalyst can invoke:

Create a markdown file at `~/.claude/agents/your-agent.md` (global) or `.claude/agents/your-agent.md` (project-scoped).

Format the frontmatter to declare its purpose:

Markdown

```
---
name: doc-writer
description: Writes inline documentation and comments for files when code is updated.
model: claude-sonnet-4-6
tools: [Read, Edit]
---
You are a technical documentation specialist. Analyze the selected files and add clean docstrings...

```


When your Nimbalyst session encounters a task matching that description, Claude Code will seamlessly delegate it to that subagent in the background.

2. Nimbalyst Parallel Sessions (External Multi-Tasking)

While subagents handle scoped delegation within a single thread, Nimbalyst’s primary layout relies on running **multiple parallel sessions** managed via its visual Kanban board.

**Subagents:** One session delegating to a throwaway context to save its own context window limits.

**Parallel Sessions:** Independent Claude Code instances running side-by-side. Nimbalyst uses **git worktrees** to isolate these sessions, meaning you can have one card on your Kanban board refactoring an auth flow while another card in a separate lane updates your database schema concurrently—without their changes or context windows colliding.

They compose perfectly: you can have three independent sessions running on your Nimbalyst Kanban board, and each individual session can spin up internal subagents as needed to crunch complex tasks.
