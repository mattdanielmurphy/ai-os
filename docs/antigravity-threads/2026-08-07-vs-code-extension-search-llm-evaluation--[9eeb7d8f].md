---
title: "VS Code Extension Search & LLM Evaluation"
date: "2026-08-07"
conversation_id: "9eeb7d8f2dc4e1ad"
source: "antigravity"
---

# VS Code Extension Search & LLM Evaluation

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-06 20:29 MDT-6] [context to this point is 0] I need a better Vscode extension search.

And I'm wondering if it's possible to copy all the search results that fit my filters and have an LLM tell me which ones I should probably consider most

---

## Assistant

The short answer is yes, absolutely. We can combine a command-line search to get the exact data you want and then pass it to an LLM to evaluate.

The VS Code Marketplace doesn't have a direct, officially supported CLI for exporting search results in a format like CSV or JSON natively. However, there are two great ways to achieve what you're looking for, depending on how much setup you want to do.

Method 1: The Open VSX API (Fastest & Cleanest)

Since you are using a local setup with an LLM and want a programmatic way to get a list of extensions, you can query **Open VSX**. It's an open-source registry (maintained by the Eclipse Foundation) used as the backend for VSCodium and other open-source editors. It mirrors the vast majority of the VS Code Marketplace and has a well-documented, accessible REST API.

**Search the API:** You can use `curl` to query their search endpoint, specifying filters like category, tags, or sort order.

**Format the Output:** Pipe the result through `jq` to extract just the relevant information (name, description, publisher, and download count) into a clean JSON array.

**Evaluate:** Pass that JSON array as context to your preferred LLM prompt (e.g., using `llm` or `sgpt` in your terminal) and ask it to evaluate the extensions based on your specific criteria.

**Example Command (Bash/Zsh):**

Bash

```
# 1. Search Open VSX for "python" extensions, sort by installs
curl -s "https://open-vsx.org/api/-/search?query=python&sortBy=installs&sortOrder=desc&size=10" | \
# 2. Parse the JSON to get a clean list
jq '[.extensions[] | {name: .name, publisher: .publisher, description: .description, installs: .downloadCount}]' > ./tmp/extensions_list.json

# 3. Ask your local LLM to evaluate (assuming you have a CLI tool like 'llm' installed)
cat ./tmp/extensions_list.json | llm "Review these VS Code extensions for Python development. Tell me which 3 are most essential for a beginner and why, ignoring formatting tools."

```

Method 2: The "Export Search Results" Extension (If you prefer the UI)

If you'd rather do your searching inside the VS Code editor itself using its built-in filters (`@category`, `@popular`, etc.), there is a community extension specifically built for this.

**Install the Extension:** Look for **Export Search Results to CSV** by Elayaraja Subramanian (ID: `ElayarajaSubramanian.export-to-csv`).

**Search:** Perform your search in the Extensions view as normal.

**Export:** Run the command `Export Search Results to CSV` from the Command Palette.

**Evaluate:** You can then feed that CSV file into your LLM for evaluation.

Want to set up a script to automate this?
Yes

---
