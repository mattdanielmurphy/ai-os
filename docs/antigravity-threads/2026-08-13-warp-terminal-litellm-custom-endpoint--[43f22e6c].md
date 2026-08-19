---
title: "Warp Terminal LiteLLM Custom Endpoint"
date: "2026-08-13"
conversation_id: "43f22e6ca156b485"
source: "antigravity"
---

# Warp Terminal LiteLLM Custom Endpoint

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-13 00:12 MDT-6] [context to this point is 0]  how do I add my litellm as a custom endpoint to warp terminal app when it doesn't accept HTTP?

---

## Assistant

Warp mandates an **`https://`** scheme for custom provider URLs in its configuration UI (located under **Settings > AI > Custom Endpoint**). If you enter `http://localhost:4000` or an HTTP IP, the interface rejects it.

To connect a local LiteLLM proxy instance, you have two core approaches: route LiteLLM through a local HTTPS reverse proxy or expose it via an SSL tunnel.

Method 1: Local Reverse Proxy with Caddy (Recommended)

Caddy automatically handles local SSL certificate generation (via trust store installation) and proxies traffic to LiteLLM without needing external network exposure.

1
Install Caddy
Use homebrew or bun to manage Caddy locally
Bash

```
brew install caddy

```

2
Generate a local domain and run Caddy

Create a standard local host mapping or route directly to `localhost` using Caddy's inline reverse proxy:

Bash

```
caddy reverse-proxy --from localhost:8443 --to localhost:4000

```


*Note: Caddy generates a self-signed TLS certificate for `localhost` and attempts to trust it locally.*

3
Configure Warp Terminal

Open Warp Settings (`Cmd + ,`) → **AI** → **Custom OpenAI API Endpoint**:

**Base URL:** `https://localhost:8443/v1`

**API Key:** Your LiteLLM key (or any dummy string if auth is disabled in LiteLLM).

Method 2: Local SSL Tunnel via `cloudflared` or `ngrok`

If local TLS verification fails inside Warp's Rust networking stack, setting up an HTTPS tunnel creates a valid, publicly trusted SSL endpoint pointing back to your LiteLLM instance.

Using Cloudflare Tunnels (Free & Quick)

Start your LiteLLM server on port 4000:

Bash

```
litellm --config config.yaml --port 4000

```


Run `cloudflared` to expose port 4000 over HTTPS:

Bash

```
npx cloudflared tunnel --url http://localhost:4000

```


Copy the generated `https://<random-subdomain>.trycloudflare.com` URL.

Set Warp's **Custom Endpoint** to:

Plaintext

```
https://<random-subdomain>.trycloudflare.com/v1

```

Method 3: Self-Signed Certs directly in LiteLLM

If you prefer to run LiteLLM directly without intermediary proxies, pass SSL certificate files directly to the LiteLLM CLI or Python script using `mkcert`:

**Generate certificates using `mkcert`:**

Bash

```
brew install mkcert
mkcert -install
mkcert localhost 127.0.0.1 ::1

```


This generates `localhost+2.pem` (cert) and `localhost+2-key.pem` (key).

**Launch LiteLLM with SSL options:**

Bash

```
litellm --config config.yaml \
  --port 4000 \
  --ssl_certfile ./localhost+2.pem \
  --ssl_keyfile ./localhost+2-key.pem

```


Enter `https://localhost:4000/v1` in Warp's Endpoint settings.

Key Warp Configuration Requirements
Setting	Value
**API Endpoint**	Must include `/v1` suffix (e.g., `https://localhost:8443/v1`)
**Protocol Requirement**	Explicitly `https://`
**Model Compatibility**	Map models in `config.yaml` to standard format (e.g., `gpt-4o`, `claude-3-5-sonnet`) so Warp routes system prompts without payload errors.
Need a template for LiteLLM's config.yaml to map models correctly?
Yes

---
