---
title: "qBittorrent Web UI Configuration Details"
date: "2026-07-28"
conversation_id: "5e7501e456c95c85"
source: "antigravity"
---

# qBittorrent Web UI Configuration Details

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




describe the config in detail. Make sure everything this screenshot shows is conveyed.

---

## Assistant

Here is a detailed breakdown of all the settings and their values shown in the screenshot for the **Web User Interface (Remote control)** configuration settings (commonly found in qBittorrent):

Main Status

**Web User Interface (Remote control)**: **Checked / Enabled**

Connection Settings

**IP address**: `*` *(binds to all available network interfaces)*

**Port**: `8080`

**Use UPnP / NAT-PMP to forward the port from my router**: **Unchecked**

**Use HTTPS instead of HTTP**: **Unchecked**

**Certificate**: *(Disabled/empty input field with a folder file-picker icon)*

**Key**: *(Disabled/empty input field with a folder file-picker icon)*

**Information link**: *Information about certificates*

Authentication Settings

**Username**: `admin`

**Password**: *(Empty text input with placeholder "Change current password")*

**Bypass authentication for clients on localhost**: **Unchecked**

**Bypass authentication for clients in whitelisted IP subnets**: **Unchecked**

**IP subnet whitelist button**: `IP subnet whitelist...` *(Disabled)*

**Ban client after consecutive failures**: **Enabled** set to `5`

**ban for**: `3600 sec`

**Session timeout**: `3600 sec`

Custom Web UI

**Use alternative Web UI**: **Unchecked**

**Files location**: *(Disabled/empty text box with folder file-picker icon)*

Security Settings

**Enable clickjacking protection**: **Checked**

**Enable Cross-Site Request Forgery (CSRF) protection**: **Checked**

**Enable cookie Secure flag (requires HTTPS)**: **Unchecked** *(Grayed out/Disabled because HTTPS is off)*

**Enable Host header validation**: **Checked**

**Server domains**: `*`

Custom Headers & Proxy Options

**Add custom HTTP headers**: **Unchecked**

**Header text area**: *(Empty box with placeholder "Header: value pairs, one per line")*

**Enable reverse proxy support**: **Unchecked**

**Trusted proxies list**: *(Disabled/partially visible text box at the bottom)*

---
