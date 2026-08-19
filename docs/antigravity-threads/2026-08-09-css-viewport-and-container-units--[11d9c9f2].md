---
title: "CSS Viewport and Container Units"
date: "2026-08-09"
conversation_id: "11d9c9f2109217fb"
source: "antigravity"
---

# CSS Viewport and Container Units

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-09 02:10 MDT-6] [context to this point is 0] what are similar css units to vw?

you know how in an element, if you do width: 100% that sets the width to its maximal space according to its parent, and that's different from 100vw?

Is there something like that but still in the vw/vw family? I believe there is

Basically a height: 100% that actually works is what I'm looking for, because height: 100% usually only works if you assign that to each parent to the very top

---

## Assistant

The unit you are looking for is **`vh` (Viewport Height)**.

Just like `100vw` ignores parent container widths and spans 100% of the browser window's width, `100vh` spans 100% of the browser window's height. It completely bypasses the need to set `height: 100%` on every parent element up to the `<html>` or `<body>` root.

However, if you've heard about new units in the "vw/vh family" recently, you are likely thinking of the **modern viewport units** introduced to fix the infamous mobile browser problem.

The Mobile `100vh` Problem and Modern Solutions

On mobile browsers (like iOS Safari or Chrome for Android), a standard `100vh` element doesn't account for the address bar or navigation toolbar expanding and collapsing. This causes `100vh` elements to actually bleed off the bottom of the visible screen when the toolbars are present.

To solve this, CSS introduced three new dynamic variants:

Unit	Name	Behavior
**`dvh`**	Dynamic Viewport Height	**(Recommended)** Adjusts dynamically as the browser UI (like the address bar) expands or retracts. `100dvh` is the safest way to get a true full-screen height on mobile.
**`svh`**	Small Viewport Height	Fixed to the *smallest* possible viewport size (when the address bar and toolbars are fully expanded).
**`lvh`**	Large Viewport Height	Fixed to the *largest* possible viewport size (when the toolbars are completely hidden/scrolled away).

*(Note: These also have width equivalents like `dvw`, `svw`, and `lvw`, though width is rarely affected by browser UI changes).*

Container Query Units (The Parent-Relative Alternative)

If you meant a unit that responds strictly to a *parent* container rather than the whole browser window, you might be thinking of **Container Query units** (`cqw`, `cqh`).

If you define a parent element as a container (`container-type: size;`), you can use `100cqh` on a deeply nested child. This equals 100% of that specific defined container's height, allowing you to bypass immediate parents without locking the sizing to the global browser window.

---
