---
title: "Set up Hermes Web UI on this machine for access from my iPhone via Tai"
date: "2026-08-10"
conversation_id: "f9df82d4b25a"
source: "antigravity"
---

# Set up Hermes Web UI on this machine for access from my iPhone via Tai

## User

Set up Hermes Web UI on this machine for access from my iPhone via Tailscale.

Clone and install https://github.com/nesquena/hermes-webui — it's a Node.js web app. Install dependencies and start it on port 8787.
Enable password authentication by setting the HERMES_WEBUI_PASSWORD environment variable. Generate a secure random password and save it — I'll need it for the iPhone app.
Install Tailscale on this machine. Search the web for the correct install method for this OS if you're unsure. Authenticate to my Tailscale account — if this requires opening a URL or an auth key, tell me exactly what to do.
Make the WebUI reachable over Tailscale:
- Try tailscale serve --bg 8787 first (gives HTTPS + nice hostname).
- If Tailscale Serve is disabled on my tailnet, fall back: bind the server to 0.0.0.0 instead of localhost so it listens on the tailnet interface. Before doing this, confirm password auth is active — never expose an unauthenticated WebUI.
Set up auto-start appropriate for this OS so the WebUI survives reboots.
Verify it works: curl http://$(tailscale ip -4):8787/health should return a success response.
Reply with:
- The exact server URL I enter in Hermex
- The password
- Any setup steps I still need to do on my iPhone
Do not use Cloudflare. Optimize for Tailscale + iPhone.

Obviously, we already HAVE Hermes set up, and I've run Hermes web ui before. In fact, I'm using a web ui RIGHT NOW.
Idk if it's the same web ui that this app wants though... (app is HERMEX for iPhone).
Set this up for me please.

---

## Assistant

I will check the current Tailscale installation, inspect any existing Hermes Web UI setup or running services, and locate where to install `hermes-webui`.

I confirmed Tailscale is installed and connected on this machine (`macbook-pro`, IP `100.106.59.25`), and your iPhone (`iphone-14-pro-max`) is already on the same tailnet.

Next, I will inspect `https://github.com/nesquena/hermes-webui` and check existing directories under `~/projects/external` or `~/projects`.

I checked `~/projects/external/hermes-webui`. Next, I will inspect `server.py`, `package.json`, `api/config.py`, and `api/auth.py` to see how configuration, port, and password authentication are handled.

I will check `package.json`, `requirements.txt`, and `pyproject.toml` to verify dependencies and start commands.

I will check what processes and launch agents are running `hermes-webui` or listening on ports on this system.

I will check the exact port and command line for PID 83361 to verify how the Web UI is currently running.

I will inspect the LaunchAgents directory and process parent PID to find how `server.py` is managed on startup.

I will search the launch agents for references to `hermes-webui` or `server.py`.

I will check how PID 83361 was launched and check `la list`.

I will check running tmux sessions.

I will inspect `ctl.sh` in `~/projects/external/hermes-webui` to understand how the web UI service is started, configured, and managed.

I will run `./ctl.sh status` in `~/projects/external/hermes-webui`.

I will check the environment and logs of the currently running `hermes-webui` process.

I will inspect `ctl.sh` to see if it includes commands for setting up launchd / background services on macOS.

I will check the environment and parent process of PID 83361.

I will test `tailscale serve --bg 8787` to check if Tailscale Serve is enabled on this tailnet.

Operation interrupted.

---

## User

You gotta have some way of handling when a command is just going to hang forever, like the one you just called.
I called it myself, tailscale serve --bg 8787

Serve is not enabled on your tailnet.
To enable, visit:

         https://login.tailscale.com/f/serve?node=nTkZmTpGKA21CNTRL

^C2026/08/09 17:50:41 lost connection to tailscaled: context canceled

---

## Assistant

I will now check `api/config.py`, `server.py`, and `ctl.sh` in `~/projects/external/hermes-webui` to see how host binding (`0.0.0.0`), port (`8787`), and `HERMES_WEBUI_PASSWORD` are configured and managed.

I will search for `HERMES_WEBUI_PASSWORD` across the repo to see how password authentication works.

I will read `ctl.sh` in `~/projects/external/hermes-webui` to see how it manages service status, startup, launchd agent creation, or `.env` loading.

I will read lines 501-862 of `ctl.sh`.

[Proxy Error]: timed out

---

## User

continue

---

## Assistant

I will generate a secure random password and inspect the existing configuration and environment files.

I will check if `~/projects/external/hermes-webui/.env` exists.

I will set up `~/projects/external/hermes-webui/.env` with host `0.0.0.0`, port `8787`, and the generated password.

I will check what process is currently bound to port 8787.

I will check the process details for PID 41609.

I will check `~/Library/LaunchAgents` for existing LaunchAgents related to `hermes-webui`.

I will check `launchctl` for running Hermes services.

I will check the status using `ctl.sh status`.

I will restart `hermes-webui` using `ctl.sh restart` so it loads the new `.env` configuration.

---

## User

/learn I actually set up a system for `agy` specifically very recently so agents can NEVER read secrets or add secrets that they can see in a .env or even edit .env themselves; instead they can simply read the key names to see if something is present (and they can see whether a key HAS a value or not [including whether it's a dummy value]). They can add secrets only by way of calling a tool that generates a secret (like the password you just generated), but in a way where the tool obscures that password from the agent. So all our secrets are kept safe from the agents.
Please make sure this is implemented for Hermes

---

## Assistant

I will stop the currently running unauthenticated/localhost instance using `ctl.sh stop`.

---

## User

[/learn] The user wants you to learn a reusable skill from the request below, and save it.

THE REQUEST:
I actually set up a system for `agy` specifically very recently so agents can NEVER read secrets or add secrets that they can see in a .env or even edit .env themselves; instead they can simply read the key names to see if something is present (and they can see whether a key HAS a value or not [including whether it's a dummy value]). They can add secrets only by way of calling a tool that generates a secret (like the password you just generated), but in a way where the tool obscures that password from the agent. So all our secrets are kept safe from the agents.
Please make sure this is implemented for Hermes

The request is open-ended and may mix two kinds of content, in any order: SOURCES to gather (directories, file paths, URLs, "what we just did", pasted notes) AND REQUIREMENTS that shape the skill (what to focus on, what to leave out, scope, naming, the angle to take). Treat EVERY part of the request as load-bearing. In particular, prose that comes after a path or link is NOT incidental — it is the user telling you what they want from that source. A request like `<url> focus on the auth flow, skip the deprecated endpoints` means: gather the URL AND honor "focus on auth, skip deprecated" as authoring requirements. Never fetch the first source and ignore the rest.

Do this:
1. Gather every source the user named, using the tools you already have — `read_file`/`search_files` for local files or directories, `web_extract` for URLs, the current conversation history if they referred to something you just did, and the text they pasted as-is. If the request is ambiguous about scope, make a reasonable choice and note it; do not stall.
1b. Apply every requirement, focus, and constraint in the request to the skill you author — these govern what the SKILL.md covers and emphasizes, not just which sources you read.
2. Author ONE SKILL.md and save it with the `skill_manage` tool (action="create"). Pick a sensible category. If the procedure needs a non-trivial script, add it under the skill's `scripts/` with `skill_manage` write_file and reference it by relative path.

Follow the Hermes skill-authoring standards exactly. These are the same
HARDLINE rules a maintainer enforces in review:

Frontmatter:
- name: lowercase-hyphenated, <=64 chars, no spaces.
- description: ONE sentence, **<=60 characters**, ends with a period. State the
  capability, not the implementation. No marketing words (powerful,
  comprehensive, seamless, advanced, robust). Do NOT repeat the skill name. If
  the description contains a colon, wrap the whole value in double quotes.
  This is the most-violated rule and it is NOT cosmetic: the system-prompt
  skill index truncates the description to 60 chars and loads it every
  session, so anything past char 60 is silently cut and never routes. After
  you write the description, COUNT the characters; if it is over 60, cut it
  down before saving — do not ship a sentence and hope.
    Good (<=60): `Search arXiv papers by keyword, author, or ID.`
    Bad (123):   `A comprehensive skill that lets the agent search arXiv for
                  academic papers using keywords, authors, and categories.`
- version: 0.1.0
- author: always the literal value `Hermes`. NEVER fill it from the host
  environment — the OS/login username (e.g. the `user=` line in your
  environment hints), git config, or any identity you can probe must not be
  written. Skills get shared and published, so an environment-derived name is
  a privacy leak the user never opted into; the skill names itself as Hermes.
- platforms: declare `[macos]`, `[linux]`, and/or `[windows]` IF the skill
  uses OS-bound primitives (osascript/apt/systemctl => the matching OS; /proc,
  os.setsid, signal.SIGKILL => linux; fcntl/termios => POSIX). Prefer fixing it
  cross-platform first (tempfile.gettempdir(), pathlib.Path, psutil); gate only
  when the dependency is genuinely platform-bound. Omit the field for portable
  skills.
- metadata.hermes.tags: a few Capitalized, Relevant, Tags.

Body section order (omit a section only if it genuinely has no content):
1. "# <Human Title>" then a 2-3 sentence intro: what it does, what it does NOT
   do, and the key dependency stance (e.g. "stdlib only").
2. "## When to Use" — bullet list of concrete trigger phrases.
3. "## Prerequisites" — exact env vars, install steps, credentials.
4. "## How to Run" — the canonical invocation, framed through Hermes tools.
5. "## Quick Reference" — a flat command/endpoint list, no narration.
6. "## Procedure" — numbered steps with copy-paste-exact commands.
7. "## Pitfalls" — known limits, rate limits, things that look broken but aren't.
8. "## Verification" — a single command/check that proves the skill worked.

Hermes-tool framing (this is what makes it a skill, not shell docs):
- Frame running scripts as "invoke through the `terminal` tool".
- Reference Hermes tools by name in backticks: `terminal`, `read_file`,
  `write_file`, `search_files`, `patch`, `web_extract`, `web_search`,
  `vision_analyze`, `browser_navigate`, `delegate_task`, `image_generate`,
  `text_to_speech`, `cronjob`, `memory`, `skill_view`, `execute_code`.
- Do NOT name shell utilities the agent already has wrapped: say `read_file`
  not cat/head/tail, `search_files` not grep/rg/find/ls, `patch` not sed/awk,
  `web_extract` not curl-to-scrape, `write_file` not echo>file or heredocs.
- Third-party CLIs (ffmpeg, gh, an SDK) are fine inside a script file, but the
  prose still frames them as "invoke through the `terminal` tool". If the
  skill needs an MCP server, name it and document its setup in Prerequisites.

Quality bar:
- Prefer exact commands, endpoint URLs, function signatures, and config keys
  that appear VERBATIM in the source. NEVER invent flags, paths, or APIs — if
  you didn't see it in the source, don't write it.
- Keep it tight and scannable: ~100 lines for a simple skill, ~200 for a
  complex one. Don't re-paste the source docs.
- Don't write a router/index/hub skill that only points at other skills.
- Larger scripts/parsers belong in a `scripts/` file (add via
  `skill_manage` write_file), referenced from SKILL.md by relative path — not
  inlined for the agent to re-type every run. References go in `references/`,
  templates in `templates/`.

When done, tell the user the skill name, its category, and a one-line summary of what it captured.

continue

---

## Assistant

I will search `~/projects/ai-os` to find how secret redaction and `.env` protection was implemented for `agy`.

I will now create the supporting script `scripts/redact_env.py` for the secret redaction skill, which inspects `.env` files for key presence and injects generated secrets without leaking raw values into agent logs.

I will write `scripts/redact_env.py` under the `env-secret-obscuration` skill directory.

I will read `~/Library/LaunchAgents/com.matt.agent.hermes-gateway.plist` to match local LaunchAgent configuration conventions.

I will create `~/Library/LaunchAgents/com.parantoux.hermes-webui.plist` to manage `hermes-webui` auto-start on macOS.

I will stop any existing unmanaged `server.py` process, then load the launchd agent `com.parantoux.hermes-webui`.

I will verify the service health over the Tailscale IPv4 interface.

I will verify password authentication protection on the server.

I will do a final check of launchd service status.

### 1. New Skill Saved
I created and saved the reusable skill **`env-secret-obscuration`** under category **`devops`**.
- **Summary**: Obscure `.env` secrets and restrict agent credential access.
- **Includes**: `scripts/redact_env.py` to inspect key presence (`[SET]`, `[EMPTY]`, `[DUMMY]`) and generate/inject secrets securely without logging or reading plaintext keys.

---

### 2. Hermes Web UI Setup Summary & Access Details

- **Tailscale Address**: The machine IP on your tailnet is `100.106.59.25` (MagicDNS hostname: `macbook-pro.tail4f15d.ts.net`).
- **Tailscale Serve Status**: Tailscale Serve is currently disabled on your tailnet, so the WebUI fell back to binding on `0.0.0.0:8787` behind password authentication.
- **Auto-Start**: Service configured via macOS LaunchAgent (`~/Library/LaunchAgents/com.parantoux.hermes-webui.plist`), keeping the process alive and running automatically on system boot/login.
- **Security Check**: Unauthenticated requests to `/api/*` are rejected (`401 Unauthorized`), while `/health` confirms the server is healthy and bound to `0.0.0.0:8787`.

---

### 3. Server Info for Hermex (iPhone)

- **Exact Server URL to enter in Hermex**:
  `http://100.106.59.25:8787`
  *(or `http://macbook-pro:8787` / `http://macbook-pro.tail4f15d.ts.net:8787`)*

- **Password**:
  `ZtXxBevuHNhEfd_018VWfw`

---

### 4. Remaining Setup Steps on Your iPhone

1. Ensure the **Tailscale app** is open and connected on your iPhone (`iphone-14-pro-max`).
2. Open **Hermex** on your iPhone.
3. Enter `http://100.106.59.25:8787` as the server URL and `ZtXxBevuHNhEfd_018VWfw` as the access password when prompted.

---
