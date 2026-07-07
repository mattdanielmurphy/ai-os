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

When you open the Agent panel (the right sidebar) or select a Claude model from Nimbalyst's interface, it will spin up the local Claude Code instance. Thanks to your `settings.json`,
