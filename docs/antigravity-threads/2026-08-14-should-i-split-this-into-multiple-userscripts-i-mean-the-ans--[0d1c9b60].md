---
title: "should I split this into multiple userscripts? I mean, the answer to: should I..."
date: "2026-08-14"
conversation_id: "0d1c9b60-c392-4adc-962b-069ff01ed029"
source: "antigravity"
---

# should I split this into multiple userscripts? I mean, the answer to: should I...

## User

should I split this into multiple userscripts?
I mean, the answer to: should I split up this massive bit of code is always yes, isn't it...
Why don't you do it for me.
The thing is, I don't want things to break.
But I've just realized, because this isn't a traditional userscript; in that it's compiled into a bundle. So I could extend this by, for massive userscripts like this, enabling them to be modular. That way they can reuse functions etc still but be split into more manageable modules.

---

## Assistant

## Perplexity — 06:29 PM

Yes—**split the source into modules, but keep one compiled userscript as the installed artifact**. That gives you readable, testable feature boundaries without breaking shared state, Tampermonkey grants, execution order, or same-page integration. Your current file already contains several largely independent subsystems—timestamps, token counting, sidebar dates, archive syncing, prompt interception, model-menu UI, slash commands, and local terminal execution—inside one IIFE.
paste.txt

What to split

Do **not** split this into separately installed userscripts. Several features share mutable state and intercept the same DOM/network events; independent scripts would make ordering and duplicated listeners much harder to control.
paste.txt

Instead, use this source layout:


```
text
gemini-thread-saver/
  src/
    index.js                   # Only composition and startup
    metadata.js                # Userscript metadata banner source
    core/
      gm.js                    # GM compatibility wrapper
      constants.js             # URLs, keys, shared selectors
      dom.js                   # Small reusable DOM helpers
      time.js                  # Date/time formatting utilities
      tooltip.js               # Shared tooltip singleton
      lifecycle.js             # Disposal registry and event helpers
    features/
      token-usage/
        tokenizer.js
        thread-messages.js
        token-badge.js
        index.js
      timestamps/
        interceptors.js        # fetch/XHR wrapping
        message-timestamps.js
        sidebar-dates.js
        prompt-timestamps.js
        index.js
      archive/
        thread-export.js
        archive-client.js
        archive-menu.js
        index.js
      prompts/
        phase-prompts.js
        slash-commands.js
        autocomplete.js
        index.js
      terminal/
        run-buttons.js
        terminal-manager.js
        context-pills.js
        index.js
      model-optimizer/
        menu-parser.js
        optimizer.js
        index.js
      page-tweaks/
        tab-title.js
        remove-upsell.js
        table-styles.js
        index.js
    app/
      observer.js
      settings-menu.js
      styles.js
  scripts/
    build.mjs
  dist/
    gemini-thread-saver.user.js
```


This maps closely to the existing section markers in the script, so the first pass is mostly **move code without redesigning it**. The source already groups these capabilities with comments such as “Token Counter,” “Sidebar Dates,” “Prompt Timestamp Prepend,” “Gemini Model Optimizer,” “Terminal Output Attachment,” and “Private Local Markdown Archive.”
paste.txt

Preserve the safety boundary

The critical rule is: **first refactor mechanically; only then improve design**. Do not combine the token logic, rewrite selectors, change timings, rename storage keys, or “clean up” event semantics during extraction.

Keep these interfaces stable:

Existing behavior	Preserve exactly
Storage keys	`gwd_*`, `gmt_thread_*`, and `gmt_archive_secret`
Local server API	`http://127.0.0.1:3033` endpoints, headers, payload shapes
Userscript permissions	Current `@grant`, `@connect`, `@match`, and `@run-at document-start` metadata
Network hooks	One owner for `XMLHttpRequest.prototype.open/send` and `window.fetch` wrapping
DOM identity	Existing IDs/classes such as `gm-timestamp`, `gmt-token-usage-badge`, `run-btn-gmt`, and `gmt-context-pills-container`
Timings	Existing 80 ms submit re-trigger, 250 ms observer debounce, 1.5 s initial archive attempt, and polling intervals

Those are integration contracts in the current script: changing them at the same time as file boundaries would make regressions difficult to localize.
paste.txt

The composition root

Your `src/index.js` should be deliberately boring: create shared dependencies once, initialize features once, and own cleanup.


```
js
import { createGm } from "./core/gm.js"
import { createTooltip } from "./core/tooltip.js"
import { createSettings } from "./app/settings-menu.js"
import { startPageObserver } from "./app/observer.js"

import { createTokenUsage } from "./features/token-usage/index.js"
import { createTimestamps } from "./features/timestamps/index.js"
import { createArchive } from "./features/archive/index.js"
import { createPrompts } from "./features/prompts/index.js"
import { createTerminal } from "./features/terminal/index.js"
import { createModelOptimizer } from "./features/model-optimizer/index.js"
import { createPageTweaks } from "./features/page-tweaks/index.js"

;(function () {
  "use strict"

  const gm = createGm()
  const tooltip = createTooltip()
  const settings = createSettings({ gm })

  const archive = createArchive({ gm })
  const tokenUsage = createTokenUsage({ getConversationId: archive.getConversationId })
  const timestamps = createTimestamps({ tooltip })
  const terminal = createTerminal({ gm })
  const prompts = createPrompts({ tokenUsage, terminal })
  const pageTweaks = createPageTweaks()
  const optimizer = createModelOptimizer()

  settings.start()
  timestamps.start()
  tokenUsage.start()
  archive.start()
  prompts.start()
  terminal.start()
  optimizer.start()

  startPageObserver({
    onUpdate() {
      timestamps.refresh()
      pageTweaks.refresh()
      prompts.refresh()
      terminal.refresh()
      optimizer.refresh()
      archive.scheduleAutoExport()
    },
  })
})()
```


The meaningful difference is dependency direction: `index.js` wires modules together; feature modules do not reach sideways into arbitrary globals. This matters here because the present file has cross-feature coupling—for example prompt submission reads token usage, the observer invokes archive/UI/run-button work, and terminal state is injected into prompts.
paste.txt

Build one userscript

Use a normal bundler and emit one `.user.js` file. Since you want a bundled userscript rather than native browser module loading, **esbuild** is a good fit: fast, simple, and it can preserve your IIFE target.


```
js
// scripts/build.mjs
import { build } from "esbuild"
import { readFile, mkdir } from "node:fs/promises"

const banner = await readFile("src/metadata.js", "utf8")
await mkdir("dist", { recursive: true })

await build({
  entryPoints: ["src/index.js"],
  outfile: "dist/gemini-thread-saver.user.js",
  bundle: true,
  format: "iife",
  target: ["chrome120"],
  banner: { js: banner },
  sourcemap: "inline",
  minify: false,
  legalComments: "none",
})
```


```
js
// src/metadata.js
// ==UserScript==
// @name         Gemini Thread Saver
// @namespace    local.gemini.thread.saver
// @version      5.1.0
// @description  Gemini timestamps and private local Markdown archive.
// @match        https://gemini.google.com/*
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_registerMenuCommand
// @grant        GM_unregisterMenuCommand
// @grant        GM_xmlhttpRequest
// @grant        GM.getValue
// @grant        GM.setValue
// @grant        GM.xmlHttpRequest
// @connect      127.0.0.1
// @run-at       document-start
// ==/UserScript==
```


Keep the metadata banner at the very beginning of the generated output. Your current script depends on `document-start`, GM storage/menu/XHR permissions, and access to `127.0.0.1`; those must remain attached to the single installed bundle.
paste.txt

Migration sequence

**Put the current file under Git unchanged**, tag it `v5.0.0`, and ensure the built output is byte-for-byte equivalent in behavior before deleting the old file.

**Extract `core/time.js`, `core/tooltip.js`, and token estimation first.** They have relatively clear boundaries and broad reuse. The current implementation already centralizes time formatting and a tooltip singleton.
paste.txt

**Extract timestamp handling as one feature**, including fetch/XHR interception, embedded prompt timestamps, message injection, and sidebar date parsing. Do not let separate modules independently patch `fetch` or `XMLHttpRequest`.
paste.txt

**Extract archive and terminal code next**, retaining the exact request URLs, archive key, and payload structure. The current code communicates with the local service for archive writes, command execution, session output, and stdin.
paste.txt

**Extract prompt enhancements**, including phase prompts, slash-command replacement, autocomplete, timestamp prepending, and terminal-context injection. These currently interact directly during Enter/click submit handling.
paste.txt

**Move observer coordination last.** Your observer is presently the global scheduler for timestamp parsing, sidebar rendering, title updates, upsell removal, prompt UI, command buttons, and archive export detection; treat it as orchestration, not a feature module.
paste.txt

After every extraction, compare the generated `dist/*.user.js` behavior manually on a real Gemini thread before proceeding.

Two changes worth making immediately

Even before the larger refactor, I would make these structural corrections:

Create a dedicated `network-interceptors` module that installs the fetch/XHR patches **once** and exposes subscription callbacks. Your script currently patches both prototypes directly in the main body; that is too high-risk to duplicate accidentally during future modular work.
paste.txt

Replace anonymous `setInterval`, document listeners, and observers with feature `start()`/`stop()` methods. You already explicitly disconnect a prior model optimizer observer via `window[OPTIMIZER_SCRIPT_ID]`; applying that lifecycle discipline consistently will prevent reload duplication.
paste.txt

So: the answer is not “multiple userscripts.” It is **one userscript distribution, modular source, a single initialization root, and a staged extraction with no behavioral edits per step**. That is the route that makes this maintainable without turning a working Gemini integration into a debugging project.

---

## User

I knew I'd have to explain this to you.
I'm already running a bundler. So splitting it into different userscripts isn't REALLY changing anything, because they're all one userscript by the time Tampermonkey sees it.

```
# Userscript Bundler

A Node.js-based automation system that creates a single, CSP-safe JavaScript bundle for Tampermonkey userscripts. This system allows you to manage multiple userscripts locally and have them dynamically loaded based on the current page URL.

## Purpose

This bundler solves the problem of managing multiple userscripts in Tampermonkey by:

1. **Avoiding CSP errors**: Creates a single bundled file that can be loaded via `@require`
2. **Dynamic loading**: Automatically executes the appropriate script based on the current page URL
3. **Easy management**: Add new userscripts without manually updating Tampermonkey configurations
4. **Local development**: Edit scripts locally and have them automatically bundled

## How It Works

### 1. Master Userscript

You install one master userscript in Tampermonkey that loads the bundled file:

```javascript
// ==UserScript==
// @name Local Userscript Dynamic Loader
// @version 0.1
// @description Loads local userscripts from bundle in ~/projects/userscript-bundler
// @match *://*/*
// @run-at document-start
// @require file:///Users/matt/projects/userscript-bundler/userscript_bundle.js
// @grant GM.getValue
// @grant GM.setValue
// @grant GM.xmlHttpRequest
// @grant GM_addElement
// @grant GM_addStyle
// @grant GM_getResourceText
// @grant GM_getValue
// @grant GM_registerMenuCommand
// @grant GM_setClipboard
// @grant GM_setValue
// @grant GM_unregisterMenuCommand
// @grant GM_xmlhttpRequest
// @grant unsafeWindow
// @connect 127.0.0.1
// ==/UserScript==
```

### 2. Source Scripts

Create individual JavaScript files for different websites or functionalities. Each script contains immediately executing code (not wrapped in functions).

### 3. Manifest Configuration

Define which scripts should run on which URLs using `script_manifest.json`.

### 4. Bundling Process

Run `node bundler.js` to:

- Read all source scripts
- Wrap each script in a unique function
- Generate a dispatcher that checks the current URL
- Create a single `userscript_bundle.js` file

### 5. Dynamic Execution

The bundled file automatically:

- Checks the current page URL
- Matches it against configured patterns
- Executes the appropriate script function i

## File Structure

```
userscript-bundler/
├── README.md # This file
├── AUTO-BUNDLING.md # Auto-bundling documentation
├── bundler.js # Main bundling script
├── watch-and-bundle.js # File watcher for auto-bundling
├── setup-auto-bundler.sh # Auto-bundling setup script
├── test-watcher.sh # Test script for file watcher
├── com.mattmurphy.userscript-bundler.plist # LaunchAgent configuration
├── userscripts/ # Source scripts directory
│ ├── source_script_a.js # Example script for GitHub
│ ├── source_script_b.js # Example script for Wikipedia
│ └── youtube search exclude terms.js # Example YouTube script
└── userscript_bundle.js # Generated output (created by bundler)
```

## Usage

### Manual Bundling

1. **Create your source scripts**:
- Add JavaScript files to the `userscripts/` directory
- Include proper userscript headers with `@name` and `@match`
- Write immediately executing code (no manual function wrapping)
- Include logging to confirm execution

2. **Generate the bundle**:

```bash
node bundler.js
```

3. **Install in Tampermonkey**:
- Create a new userscript with the master template
- Update the `@require` path to point to your `userscript_bundle.js`

### Automatic Bundling (Recommended)

For seamless development, set up automatic bundling that watches for file changes:

1. **Set up auto-bundling**:

```bash
./setup-auto-bundler.sh
```

2. **Edit and save userscripts**:
- The bundle automatically updates when you save `.js` files
- No need to manually run the bundler
- See `AUTO-BUNDLING.md` for complete documentation

3. **Add new scripts**:
- Create new source files in `userscripts/`
- Include proper userscript headers
- The bundle automatically updates
- No need to update Tampermonkey!

## Example Source Scripts

### GitHub Script (`source_script_a.js`)

```javascript
console.log("GitHub script loaded!")
// Add GitHub-specific functionality here
```

### Wikipedia Script (`source_script_b.js`)

```javascript
console.log("Wikipedia script loaded!")
// Add Wikipedia-specific functionality here
```

## Manifest Configuration

```json
[
{
"file": "source_script_a.js",
"match": "github.com"
},
{
"file": "source_script_b.js",
"match": "wikipedia.org"
}
]
```

## Benefits

- **No CSP issues**: Single bundled file avoids Content Security Policy restrictions
- **Easy maintenance**: Add/remove scripts without touching Tampermonkey
- **Local development**: Edit scripts in your preferred editor
- **Automatic bundling**: File watcher automatically rebuilds when you save changes
- **URL-based routing**: Scripts automatically run on the right pages
- **System integration**: Auto-bundling runs as a macOS LaunchAgent (starts with your Mac)
- **Zero manual work**: Just edit and save - everything else is automatic

## Technical Details

The bundler:

1. **Auto-generates manifest** from userscript headers (`@name` and `@match`)
2. **Wraps each source script** in a unique function name with DOM ready logic
3. **Creates a dispatcher** that checks `window.location.href`
4. **Uses simple string matching** to determine which script to run
5. **Outputs a single, self-contained JavaScript file**

### Auto-Bundling System

- **File watcher** monitors the `userscripts/` directory for changes
- **Debounced execution** prevents rapid rebuilds during editing
- **LaunchAgent integration** runs automatically on system startup
- **Full logging** tracks all activity and errors

This approach ensures compatibility with Tampermonkey's CSP restrictions while providing a flexible, automated development workflow.

## Documentation

- **`AUTO-BUNDLING.md`** - Complete guide to the automatic bundling system
- **`README.md`** - This overview and usage guide
```

Give me a prompt to make the changes that should be made for this particular gemini.js userscript.

---

## Assistant

## Perplexity — 06:29 PM

You’re right: with your loader, this is **not** about creating separately installed Tampermonkey scripts. The change should be to give the bundler a **grouped, ordered multi-file source mode** where all Gemini files are concatenated inside one generated Gemini wrapper, preserving one shared lexical scope and therefore existing function/state access. Your current Gemini script has substantial cross-feature coupling—prompt submission reads token totals, the main observer calls several UI/archive actions, and shared mutable state is used by timestamp, archive, terminal, and UI code—so that is safer than turning every file into an isolated wrapper immediately.
paste.txt

Paste this into your coding agent:


```
text
Refactor the existing massive Gemini userscript into multiple maintainable source files while preserving its current runtime behavior exactly.

## Context

Repository: ~/projects/userscript-bundler

This project has:
- One Tampermonkey “master loader” userscript.
- A local `userscript_bundle.js` generated by `bundler.js`.
- Individual source scripts discovered and dispatched by URL.
- A file watcher that rebuilds automatically.

Important: Do NOT create multiple Tampermonkey-installed userscripts. The target remains a single generated `userscript_bundle.js` loaded through the master userscript’s `@require`.

The current Gemini source is a very large `gemini.js` / Gemini Thread Saver userscript. It runs at `document-start` on `https://gemini.google.com/*` and contains tightly connected functionality:
- Accurate-ish thread token counting and its floating badge
- GM settings menu for sidebar dates and auto archive sync
- Shared tooltip and time/date formatting utilities
- XHR/fetch interception for Gemini timestamp extraction
- Message timestamp injection and embedded prompt-timestamp parsing
- Sidebar conversation dates
- Prompt timestamp prepending and `/phase0` through `/phase3` prompt replacement
- Prompt autocomplete and phase selection UI
- Tab-title sync and page tweaks
- Gemini model menu optimizer
- Local thread archive requests to `127.0.0.1:3033`
- Bash-code-block local execution controls, inline terminal output, context pills, and terminal-input handling
- MutationObserver coordination

The current code relies on shared functions and mutable state across those areas. Do not attempt a full ESM/import-export migration in this task. The existing bundler’s source files are wrapped independently, so native isolated modules would break current cross-file references unless the bundler changes.

## Goal

Add a “script group” capability to the bundler, then split Gemini Thread Saver into ordered files belonging to one `gemini-thread-saver` group.

For a grouped script:
1. The bundler must concatenate the group’s files in an explicit deterministic order.
2. It must put the concatenated group code inside ONE generated function/IIFE wrapper.
3. All files in the group must therefore share the same lexical scope at runtime.
4. The dispatcher must invoke only the group entry wrapper when the Gemini URL matches.
5. Existing normal one-file userscripts must continue to bundle and dispatch exactly as before.
6. The generated bundle must remain self-contained and CSP-safe, with no runtime module loading, no `eval`, no dynamic `<script>` tags, and no external dependencies.

This is deliberately a behavior-preserving source-layout refactor, not a redesign.

## First: inspect before editing

Before making changes:
1. Inspect `bundler.js`, the manifest format or header-discovery logic, the watcher, and current userscript directory conventions.
2. Locate the actual Gemini source file and identify every top-level function, variable, interval, listener, observer, local-storage key, GM-storage key, DOM ID/class, local-server endpoint, and `window.*` singleton it uses.
3. Determine whether source headers are mandatory for discovery. Retain or adapt them so the Gemini group remains detected correctly.
4. Make a git branch named `refactor/gemini-grouped-source` if the repository is a git repository.
5. Do not change the master Tampermonkey loader metadata or its currently granted permissions.

## Bundler changes

Implement the smallest clean extension compatible with the current bundler design.

Preferred manifest shape, if the existing format can support it cleanly:

```json
[
  {
    "name": "Gemini Thread Saver",
    "match": "gemini.google.com",
    "group": "gemini-thread-saver",
    "files": [
      "gemini-thread-saver/00-bootstrap.js",
      "gemini-thread-saver/01-shared.js",
      "gemini-thread-saver/02-token-usage.js",
      "gemini-thread-saver/03-timestamps.js",
      "gemini-thread-saver/04-sidebar-dates.js",
      "gemini-thread-saver/05-prompt-tools.js",
      "gemini-thread-saver/06-archive.js",
      "gemini-thread-saver/07-terminal.js",
      "gemini-thread-saver/08-model-optimizer.js",
      "gemini-thread-saver/09-page-observer.js"
    ]
  }
]
```

Adapt this to the project’s actual manifest conventions if needed, but preserve these semantic requirements:
- A group has one URL match and one dispatcher entry.
- A group’s `files` array is the sole source of execution order.
- Each file is read as raw JavaScript and concatenated into the same generated wrapper scope.
- The bundle includes clear source-boundary comments such as:
  `/* ===== gemini-thread-saver/03-timestamps.js ===== */`
- Fail the build with a useful error if a grouped source file is missing, duplicated, unreadable, or escapes the configured source directory.
- Preserve the behavior of current simple manifest entries and auto-discovered standalone scripts.
- Update the watcher so edits anywhere under grouped directories trigger a rebuild.
- Update README documentation with concise grouped-userscript usage and an example.

Do not make the grouped files independently dispatchable. They are parts of one Gemini application.

## Gemini file layout

Create this directory under the existing userscripts source directory:

```text
userscripts/
  gemini-thread-saver/
    00-bootstrap.js
    01-shared.js
    02-token-usage.js
    03-timestamps.js
    04-sidebar-dates.js
    05-prompt-tools.js
    06-archive.js
    07-terminal.js
    08-model-optimizer.js
    09-page-observer.js
```

Use numeric prefixes for explicit load order. Do not rely on filesystem ordering.

Move existing code mechanically into these files:

### `00-bootstrap.js`
- Keep the Gemini userscript metadata/header only if the current discovery system requires it.
- Start the existing outer IIFE and `"use strict"` exactly once.
- Keep any compatibility/global setup that must execute before all other code.
- Do not close the IIFE here; close it only in `09-page-observer.js`.
- Add a short comment explaining that every grouped file is concatenated into this one shared lexical scope.

### `01-shared.js`
- GM compatibility wrapper/state if present
- Shared constants
- `FONT`
- Shared tooltip singleton
- Shared date/time helpers
- Common DOM/query helpers only where they already exist
- Do not introduce broad new abstractions

### `02-token-usage.js`
- `estimateTokensAccurate`
- Scroll-container and thread-message collection
- Thread token calculation, anchor/cache behavior, and token badge UI
- Preserve all localStorage keys, DOM IDs, polling interval, styles, thresholds, output strings, and precision behavior

### `03-timestamps.js`
- Timestamp regex/state
- Fetch/XHR interception
- Sidebar-URL detection
- Message timestamp extraction
- Heuristic timestamp injection
- Embedded timestamp parsing and cleanup
- Preserve the existing prototype patching behavior, selector behavior, intervals, and timestamp display semantics

### `04-sidebar-dates.js`
- Sidebar date map/parsing
- Absolute/relative sidebar rendering
- Sidebar settings state and GM menu registration
- Sidebar rerendering
- Preserve all GM storage keys, menu labels, item selectors, CSS class names, and layout behavior

### `05-prompt-tools.js`
- Prompt timestamp prepending
- Send-button discovery
- Click and Enter submission interception
- Phase prompt constants
- Slash-command replacement
- Autocomplete UI
- Phase selector UI
- Existing injected styles related to prompt tooling
- Preserve current event capture/bubble behavior, stopPropagation/preventDefault behavior, re-trigger timing, command names, and exact prompt text

### `06-archive.js`
- Thread ID/title/message extraction
- Local Markdown archive behavior
- Archive notices
- Archive menu commands
- Export scheduling helpers
- Preserve every request URL, header name, request body field, secret/storage key, debounce/timing value, archive signature behavior, and server response handling

### `07-terminal.js`
- Bash run-button injection
- Trusted Types SVG helper/policy behavior
- Local command execution requests
- Inline terminal output
- Session polling
- Terminal input
- Context pills and prompt-context injection
- Preserve every local API endpoint, header, timeout/poll interval, session behavior, UI ID/class, and current disabled/retired-backend behavior where it exists

### `08-model-optimizer.js`
- Model menu parsing
- Model selection behavior
- Thinking/extended selection behavior
- MutationObserver setup specific to the optimizer
- Preserve the existing `window[...]` optimizer singleton/disconnect behavior so duplicate initialization remains prevented

### `09-page-observer.js`
- Page tweaks such as tab-title synchronization and upsell removal
- The main mutation observer and its debounce/export logic
- Initial startup calls in their current effective order
- Close the outer IIFE started in `00-bootstrap.js`
- This file is the only place that should own the top-level orchestration observer

## Non-negotiable compatibility constraints

Do not change any of the following during this refactor:
- Gemini URL matching behavior
- Tampermonkey master loader
- Existing GM grants, GM API usage, and GM storage keys
- `127.0.0.1:3033` endpoints, paths, headers, body shapes, or expected response parsing
- `localStorage` keys such as existing thread-token cache keys
- Existing user-visible prompt text, phase prompt content, menu labels, notifications, badge text, tooltip text, or UI behavior
- Existing selectors unless moving their code requires no selector change
- Existing generated DOM IDs/classes/data attributes
- Existing `setInterval`, `setTimeout`, observer debounce, and re-trigger durations
- Existing event phases and the order in which listeners are registered
- Existing `window` singleton names and duplicate-run guards
- Existing handling of `document-start` and delayed `document.body` availability
- Existing behavior on non-Gemini sites

Avoid incidental cleanup such as renaming variables, reformatting whole modules, replacing `var`/`let`/`const`, changing async style, changing `innerText` to `textContent`, rewriting regexes, or altering CSS. Only move code and make the minimal bundler changes needed to support grouping.

## Validation requirements

After implementation:

1. Run the project’s normal bundle command.
2. Verify the generated `userscript_bundle.js` includes:
   - Exactly one Gemini dispatcher entry
   - Exactly one Gemini wrapper function/IIFE
   - All Gemini source-boundary comments
   - All ten Gemini sections in manifest order
3. Verify normal standalone userscripts still appear in the output and retain their old dispatch behavior.
4. Run a syntax check on the generated bundle.
5. Add a small Node-based regression test or fixture for grouped bundling if this repository has any test convention; otherwise add `test-grouped-bundle.js` that:
   - Builds a minimal two-file grouped fixture
   - Confirms lexical sharing works (`const`/function declared in file one is used in file two)
   - Confirms group order is preserved
   - Confirms the dispatcher calls the group once
   - Confirms missing grouped files fail clearly
6. Search the generated bundle to ensure these expected Gemini symbols still exist exactly once where appropriate:
   - `estimateTokensAccurate`
   - `calculateThreadTokens`
   - `processEmbeddedTimestamps`
   - `extractSidebarTimestamps`
   - `exportThreadWithTimestamps`
   - `terminalManager`
   - `startOptimizer`
   - `startObservers`
7. Produce a concise final report containing:
   - Files added, moved, and changed
   - The finalized group manifest/configuration entry
   - The build and test commands run
   - Any behavior that could not be verified without loading Gemini in a browser
   - Confirmation that no Tampermonkey installation changes are required

Do not stop after proposing a plan. Make the edits, run the validation, and leave the repository in a buildable state.
```


The key specification is “concatenate ordered source fragments into one group wrapper,” rather than independently wrapping each Gemini fragment. That preserves lexical access to things such as `calculateThreadTokens`, `autocompleteMenu`, archive helpers, the shared tooltip, `terminalManager`, and observer callbacks while giving you sane files to work in.
paste.txt

---

## User

ok great.
Now, I figure I should go through the rest of my userscripts and do the same for each of them?
What about having shared components across the userscripts? Like UI components for example

---

## Assistant

## Perplexity — 06:29 PM

Yes—but **not as a blanket “split every userscript” refactor**. Apply the grouped-source pattern to scripts that are large, actively changed, or contain distinct features with shared state; leave small focused scripts as one file. You already prefer maintainable scoped modules and a fast local workflow, so grouped scripts plus a small shared library is a good fit.

Use three layers

```
text
userscript-bundler/
  userscripts/
    _shared/
      dom.js
      styles.js
      ui/
        tooltip.js
        toast.js
        modal.js
        icons.js
      gm.js
      lifecycle.js

    gemini-thread-saver/
      00-bootstrap.js
      ...
      09-page-observer.js

    youtube-tools/
      00-bootstrap.js
      01-video-tools.js
      02-ui.js
      99-start.js

    simple-site-tweak.js

  script_manifest.json
  userscript_bundle.js
```


**Standalone scripts**: Keep short, single-purpose scripts as a normal one-file entry.

**Grouped apps**: Use your new ordered shared-scope group mechanism for large, multi-feature scripts such as Gemini.

**Shared library**: Use source files that the bundler can prepend into a target group wrapper before that group’s own files.

The useful threshold is not raw line count; it is whether a change requires you to understand several unrelated regions of the file. Gemini clearly crosses that line because it combines DOM observers, network interception, GM settings, archive integration, terminal execution, timestamps, and multiple UI systems.
paste.txt

Share utilities, not features

Make `_shared` for code that is **site-agnostic and stateless, or explicitly factory-based**:

Good shared component	Keep site-specific
`createTooltip()`	Gemini sidebar date renderer
`showToast()`	Gemini archive status notices
`createModal()`	Gemini model-menu replacement
DOM helpers such as `waitForElement()`	Gemini’s brittle selector knowledge
`addStyleOnce()`	Per-site visual layout rules
GM API compatibility adapter	Per-script storage keys and menu behavior
`createDisposer()`	A particular script’s observer policy
SVG/icon helpers	Script-specific action buttons

Do **not** turn “all UI” into a global framework. A shared tooltip, toast, modal, icon helper, and stylesheet injector are worthwhile; a generic component architecture for every one-off injected button often creates more indirection than it removes.

Avoid shared global collisions

The important change: each userscript group should get a private namespace, even when shared helpers are available.

Instead of letting shared files declare globals such as:


```
js
let tooltipEl = null
function showTooltip() {}
```


make them expose factories:


```
js
// _shared/ui/tooltip.js
function createTooltip({ className = "us-tooltip", zIndex = 999999 }) {
  let element = null

  function ensure() {
    if (element?.isConnected) return element

    element = document.createElement("div")
    element.className = className
    element.style.zIndex = String(zIndex)
    document.body.appendChild(element)
    return element
  }

  return {
    show(event, text) {
      const el = ensure()
      el.textContent = text
      el.hidden = false
      el.style.left = `${event.clientX + 12}px`
      el.style.top = `${event.clientY + 12}px`
    },
    hide() {
      if (element) element.hidden = true
    },
    destroy() {
      element?.remove()
      element = null
    },
  }
}
```


Then Gemini owns its instance:


```
js
const geminiTooltip = createTooltip({
  className: "gmt-tooltip",
  zIndex: 99999,
})
```


That prevents YouTube tooling, Gemini tooling, and a future site script from accidentally sharing state or removing one another’s DOM nodes. Gemini’s current tooltip is a singleton with module-level state, so it is a strong first candidate for conversion into a reusable factory—but do that **after** the mechanical split is stable.
paste.txt

Extend the manifest

Give each grouped app an explicit `shared` field. The bundler should concatenate shared files **inside that script group’s wrapper**, before its own ordered files.


```
json
[
  {
    "name": "Gemini Thread Saver",
    "match": "gemini.google.com",
    "group": "gemini-thread-saver",
    "shared": [
      "_shared/gm.js",
      "_shared/dom.js",
      "_shared/styles.js",
      "_shared/lifecycle.js",
      "_shared/ui/tooltip.js",
      "_shared/ui/toast.js"
    ],
    "files": [
      "gemini-thread-saver/00-bootstrap.js",
      "gemini-thread-saver/01-shared.js",
      "gemini-thread-saver/02-token-usage.js",
      "gemini-thread-saver/03-timestamps.js",
      "gemini-thread-saver/04-sidebar-dates.js",
      "gemini-thread-saver/05-prompt-tools.js",
      "gemini-thread-saver/06-archive.js",
      "gemini-thread-saver/07-terminal.js",
      "gemini-thread-saver/08-model-optimizer.js",
      "gemini-thread-saver/09-page-observer.js"
    ]
  }
]
```


Conceptually, generate this:


```
js
function run_gemini_thread_saver() {
  "use strict"

  /* _shared/dom.js */
  /* _shared/ui/tooltip.js */
  /* gemini-thread-saver/00-bootstrap.js */
  /* ... */
}
```


Do **not** place shared files at the top of the whole global bundle. If you do, every script can collide through shared top-level names, and mutable UI state will leak across unrelated apps.

Add a lifecycle helper

Most userscript breakage during SPAs/reloads comes from duplicate listeners, intervals, observers, and injected nodes. A tiny shared disposer is more valuable than a big UI library:


```
js
// _shared/lifecycle.js
function createDisposer() {
  const cleanups = []

  return {
    add(cleanup) {
      cleanups.push(cleanup)
      return cleanup
    },

    listen(target, type, handler, options) {
      target.addEventListener(type, handler, options)
      this.add(() => target.removeEventListener(type, handler, options))
      return handler
    },

    interval(callback, delay) {
      const id = setInterval(callback, delay)
      this.add(() => clearInterval(id))
      return id
    },

    timeout(callback, delay) {
      const id = setTimeout(callback, delay)
      this.add(() => clearTimeout(id))
      return id
    },

    observer(observer) {
      this.add(() => observer.disconnect())
      return observer
    },

    dispose() {
      while (cleanups.length) cleanups.pop()()
    },
  }
}
```


It would help scripts that inject UI repeatedly into dynamic sites. For Gemini specifically, it gives a disciplined path for its token polling, heuristic timestamp polling, optimizer observer, main observer, and document listeners, though those should stay untouched in the first split.
paste.txt

Practical rollout

**Finish Gemini’s grouped split first**, with no shared-library extraction.

Make a `_shared` directory containing only duplicated helpers you can identify in at least **two** scripts.

Convert shared helpers to factories or pure functions; never import a shared singleton with hidden state.

Migrate one script at a time, leaving its behavior unchanged.

Add a bundle test that builds two grouped scripts using the same shared helper and proves their state is isolated.

Keep a “simple scripts stay single-file” rule. A 100–300 line narrow site tweak does not need a mini-app architecture.

The main test for a new shared component is: **could it be copied into another script with no site selectors, storage key assumptions, endpoint assumptions, or hidden global state?** If yes, share it; otherwise keep it owned by its userscript.

---

## User

ok gemini is split.
Now give me a prompt to transform the rest of the userscripts according to best practices.
You know it just occurred to me; with so much being changed at once, it's possible things will break. It'd be great if we could add per-userscript version control via a master interface.
I already have the Tampermonkey menu for enabling/disabling userscripts, but it could be nicer.
A custom interface that we can make appear on any site to configure our userscripts, possibly roll back, that would be nice.

---

## Assistant

## Perplexity — 06:29 PM

Yes: add a **bundled control plane** now, before refactoring the rest. The useful rollback design is not Git access from the browser; it is a per-userscript release registry embedded in the generated bundle, with the selected release stored in GM storage and applied after a page reload. That lets you revert one script without reverting every other script or editing Tampermonkey.

Paste this into your coding agent:


```
text
Upgrade ~/projects/userscript-bundler so it can safely modularize the remaining userscripts and provide a cross-site Userscript Control Center with per-userscript enablement, release selection, rollback, and diagnostics.

Gemini Thread Saver has already been converted into an ordered grouped userscript. Treat that grouped implementation as the reference architecture and do not rework it unless required for compatibility with this new control plane.

This is a real implementation task. Inspect the repository first, then make the changes, run validation, and leave it buildable.

# Core outcome

The system must still have:
- One Tampermonkey master loader
- One generated local bundle loaded through `@require`
- No runtime external script loading
- No `eval`, `Function`, dynamic `<script>` injection, or network dependency for normal script execution
- CSP-safe generated JavaScript
- Normal execution at `document-start`

Add:
1. Grouped modular source support for complex userscripts
2. A shared utility/component layer that is isolated per userscript runtime
3. A cross-site Userscript Control Center
4. Per-userscript release history and rollback
5. Per-userscript enable/disable overrides
6. Error reporting and useful diagnostics
7. Safe migration behavior so a bad refactor does not disable the entire bundle

# Important architecture decision

Do NOT create separate Tampermonkey-installed scripts.

Do NOT try to make the browser read Git history directly.

Instead, make the bundler generate a script registry that contains:
- The current release for each userscript
- A bounded number of prior generated releases for each userscript
- A stable script ID
- Human-readable name and description
- Match patterns
- Release metadata
- Per-release runner functions

At runtime:
- The control center stores per-script configuration with GM storage.
- The dispatcher checks whether the script is enabled.
- The dispatcher selects the configured release, defaulting to `current`.
- The selected embedded release function runs only if the current URL matches.
- A release change takes effect after a normal page reload.
- Each script is independently try/catch wrapped so failure in one script does not prevent other matching scripts from running.

This permits a rollback of just one broken userscript even after the bundle has been rebuilt.

# Preserve existing behavior

Do not change:
- The master Tampermonkey loader metadata, grants, `@require`, or `@connect` configuration
- Existing normal standalone-script dispatch behavior except where the new registry/enablement/release gate is required
- Gemini Thread Saver behavior, selectors, timings, local endpoints, GM storage keys, archive logic, DOM IDs/classes, user-visible strings, or its grouped file ordering
- Existing script behavior during mechanical source splitting
- Existing source discovery behavior unless extended compatibly
- Existing generated bundle location
- Existing automatic watcher/LaunchAgent workflow

Do not invent a second build system. Continue using the project’s actual Node-based bundler and watcher.

# First inspect and document

Before implementation:
1. Inspect `bundler.js`, watcher code, manifest handling, userscript headers, generated bundle layout, and all current source scripts.
2. Create an inventory of every userscript:
   - proposed stable ID
   - name
   - URL match behavior
   - approximate size
   - whether it is already grouped
   - whether it needs modularization
   - likely reusable components/utilities
   - special requirements such as `unsafeWindow`, GM APIs, local endpoints, or early document-start interception
3. Write this inventory to `docs/userscript-inventory.md`.
4. Do not modularize tiny, focused scripts merely for uniformity.
5. Make a git branch named `feature/userscript-control-center` if this is a git repository.

# Script classifications

Classify scripts before changing them:

## Keep standalone
Keep a script as one source file when it is:
- small
- site-specific
- one feature
- unlikely to be changed often
- not sharing meaningful code with another script

## Convert to grouped source
Convert a script to an ordered group when it:
- contains multiple independent features
- has more than one major UI area
- uses observers, timers, network interception, or SPA navigation handling
- has several distinct stateful subsystems
- is actively changed
- is large enough that finding a feature is difficult

## Shared utilities
Move code into shared utilities only if it is used by at least two userscripts, or is clearly a generic control-plane dependency.

Do not build a generic frontend framework.

Good shared candidates:
- GM API compatibility adapter
- `addStyleOnce`
- `waitForElement`
- `observeUntilFound`
- URL/match helpers
- structured logging
- disposal/lifecycle helper
- toast factory
- modal factory
- tooltip factory
- icon/SVG helper
- keyboard shortcut helper
- Control Center UI primitives

Do not share:
- site-specific selectors
- page-specific DOM renderers
- storage keys belonging to one script
- local-server endpoints belonging to one script
- script-specific MutationObserver policies
- site-specific CSS
- hidden mutable singleton state

# Shared-code isolation rule

Shared source must NOT be concatenated once at global bundle scope.

Each selected userscript release must run in its own function wrapper. If a script declares:

```js
let state = {}
const tooltip = createTooltip()
```

that state must be private to that particular userscript/release execution.

Shared helpers should be pure functions or factories:

```js
function createToast(options = {}) {
  let container = null
  return {
    show(message, config = {}) {},
    destroy() {},
  }
}
```

Do not export global singleton UI objects shared across unrelated userscripts.

Add namespaced DOM identifiers where shared UI injects DOM:
- `uscc-*` for Control Center UI
- script-owned UI retains its existing prefixes
- avoid generic IDs such as `tooltip`, `modal`, `container`, or `toast`

# Manifest and grouped scripts

Extend the manifest in the smallest compatible way.

Support both existing standalone entries and grouped entries.

A grouped entry should support a shape equivalent to:

```json
{
  "id": "gemini-thread-saver",
  "name": "Gemini Thread Saver",
  "description": "Gemini timestamps and private local Markdown archive",
  "match": ["https://gemini.google.com/*"],
  "group": "gemini-thread-saver",
  "shared": [
    "_shared/core/dom.js",
    "_shared/core/styles.js",
    "_shared/core/lifecycle.js"
  ],
  "files": [
    "gemini-thread-saver/00-bootstrap.js",
    "gemini-thread-saver/01-shared.js",
    "gemini-thread-saver/02-token-usage.js",
    "gemini-thread-saver/03-timestamps.js",
    "gemini-thread-saver/04-sidebar-dates.js",
    "gemini-thread-saver/05-prompt-tools.js",
    "gemini-thread-saver/06-archive.js",
    "gemini-thread-saver/07-terminal.js",
    "gemini-thread-saver/08-model-optimizer.js",
    "gemini-thread-saver/09-page-observer.js"
  ],
  "releaseHistory": 5
}
```

Adapt property names to fit the actual project conventions, but preserve these semantics:
- `id` is stable and never derived from filename after the initial migration
- `files` is the only source of grouped execution order
- `shared` is concatenated inside the target script wrapper before the script’s files
- grouped files are not separately dispatchable
- reject missing, unreadable, duplicate, or out-of-root paths with clear build errors
- retain standalone userscript compatibility
- emit source-boundary comments in the generated output

Use default release history of 5, configurable globally and per script. Make 5 the default unless the repository already has a more appropriate configuration style.

# Release history and rollback

Implement build-time per-userscript snapshots.

The bundler must:
1. Produce a deterministic content hash for each script release from its effective source:
   - relevant shared source content
   - ordered source file content
   - script configuration that affects execution
2. Use that hash to avoid storing duplicate releases when no effective source changed.
3. Maintain generated release metadata in a repository file, for example:
   `state/userscript-release-history.json`
4. Store, per script:
   - stable script ID
   - release ID or content hash
   - created timestamp
   - display label
   - source file list
   - source hash
   - current flag
   - optional git short commit hash if available
5. Keep the current release plus the most recent 5 prior distinct releases by default.
6. Prune older snapshots only after the current bundle has successfully been generated.
7. Embed each retained release as its own runner function in the generated bundle.
8. Ensure a selected release remains usable after later rebuilds until it falls outside configured retention.
9. If a user has selected a release that has been pruned, safely fall back to `current`, log a clear warning, and surface it in Control Center diagnostics.
10. Do not retain secrets or environment files as snapshots. Only userscript source effective content.

Do not use `eval` to run stored source. The bundler must generate actual JavaScript runner functions statically.

Example intended generated concept:

```js
const SCRIPT_REGISTRY = {
  "gemini-thread-saver": {
    name: "Gemini Thread Saver",
    matches(url) {},
    releases: {
      "current": { id: "current", label: "Current", run() {} },
      "20260721-abc123": { id: "20260721-abc123", label: "2026-07-21 abc123", run() {} }
    },
    currentReleaseId: "current"
  }
}
```

The actual release ID format may differ, but it must be stable, readable, and unique.

# Runtime configuration

Use namespaced GM storage. Do not collide with existing userscript settings.

Recommended configuration structure:

```js
const CONTROL_CENTER_STORAGE_KEY = "uscc:config:v1"

{
  version: 1,
  scripts: {
    "gemini-thread-saver": {
      enabled: true,
      selectedReleaseId: "current"
    },
    "youtube-search-exclude-terms": {
      enabled: false,
      selectedReleaseId: "current"
    }
  },
  ui: {
    hotkey: {
      key: "U",
      alt: true,
      shift: true
    }
  }
}
```

Requirements:
- Default every registered script to enabled.
- Preserve existing Tampermonkey-level enable/disable behavior; this is an additional in-bundle gate.
- Read config early enough for document-start scripts.
- If GM async APIs are the only available API shape, create a safe compatibility layer. Do not delay document-start scripts unnecessarily.
- Validate loaded config defensively. Invalid/malformed config must reset only invalid portions, never crash the dispatcher.
- Save configuration atomically as one object where practical.
- Do not overwrite existing script-specific GM settings.

# Dispatcher and fault isolation

The generated bundle must:
1. Initialize the control-plane API.
2. Determine matching scripts for the current URL.
3. Skip disabled scripts.
4. Select the requested release, defaulting to current.
5. Run each selected script independently:
   - dedicated `try/catch`
   - error logging
   - error retained in in-memory diagnostics
   - one broken script must not stop later scripts
6. Add a small duplicate-run guard per script release per document:
   - use a clearly namespaced `window` key
   - do not conflict with existing script-specific duplicate guards
   - avoid preventing normal SPA observer behavior inside a script
7. Do not show any UI automatically on page load.

# Userscript Control Center

Build a polished, lightweight custom interface that can open on any site.

Entry points:
1. A Tampermonkey menu command named `Open Userscript Control Center`
2. Keyboard shortcut: `Alt+Shift+U`
3. Optional compact launcher only when explicitly enabled later; do not add an always-visible floating button now

The Control Center must work on arbitrary pages, including pages where no normal userscript matches.

UI requirements:
- Inject one namespaced host: `#uscc-root`
- Prefer Shadow DOM for style isolation; gracefully fall back to namespaced CSS if Shadow DOM attachment fails
- Dark, compact, keyboard-accessible interface
- Escape closes
- Focus is moved into the dialog when opened and restored when closed
- No external CSS, fonts, images, icon libraries, CDNs, or network requests
- Use inline SVG/icons only if needed
- Do not use `innerHTML` with untrusted content
- Guard against the active site’s CSS using Shadow DOM or aggressive namespacing
- Use a high z-index but do not interfere with page input while closed

Display:
- Search/filter input
- Each registered userscript:
  - enabled toggle
  - name
  - script ID
  - short description
  - match patterns
  - classification: standalone or grouped
  - current selected release
  - release selector
  - current release marker
  - compact “Reset to current” button when rolled back
  - last run status for this page: not matched / disabled / ran / failed
  - last captured error for this page, if any
- A selected-script detail panel or expandable row:
  - source file list
  - release IDs
  - release timestamps
  - source hash
  - optional git short hash
  - whether the chosen release is available
- Global actions:
  - Reload page
  - Enable all
  - Disable all
  - Reset all releases to current
  - Export configuration JSON to clipboard or downloadable blob
  - Import configuration JSON with schema validation and explicit confirmation
  - Clear in-memory diagnostic history

Behavior:
- Enable/disable and release selection save immediately.
- Clearly state: “Changes apply after reload.”
- Rollback must only affect the selected script.
- Before selecting a non-current release, show a concise confirmation that includes the script name and chosen release.
- Do not attempt to dynamically unload a script that already ran on the current page.
- Do not expose or execute arbitrary user-entered code.

# Diagnostics and logging

Add a shared structured logger, private per script runtime where possible.

Requirements:
- Consistent prefix, for example `[USCC]`
- Log script ID and selected release ID
- Capture runtime errors from script startup
- Keep a bounded in-memory ring buffer, e.g. last 100 records
- Control Center displays relevant current-page status and errors
- Do not persist full stack traces or page content by default
- Add a “copy diagnostics” action that copies a concise safe report:
  - bundle build timestamp/version
  - current URL origin only, not full URL query parameters
  - matching scripts
  - enabled/selected releases
  - current-page statuses
  - error messages and stacks if present
- Do not log secrets, GM stored values, request bodies, page text, archive contents, or terminal contents

# Mechanical modularization of remaining scripts

After the control plane and release history work, modularize the remaining scripts in order of risk, one script at a time.

For each candidate:
1. Add it to the inventory.
2. Decide whether it stays standalone or becomes grouped.
3. If grouped:
   - preserve behavior through mechanical extraction first
   - use numbered ordered files
   - maintain one shared lexical scope inside that script’s generated release wrapper
   - keep startup orchestration in a final file
4. Build and validate before moving to the next script.
5. Do not combine a behavior rewrite with source splitting.
6. Do not extract code to `_shared` during the first mechanical split unless it is already used by at least two scripts and can be made pure/factory-based without behavior changes.

Suggested grouped layout:

```text
userscripts/
  script-id/
    00-bootstrap.js
    01-shared.js
    02-feature-a.js
    03-feature-b.js
    99-start.js
```

Use meaningful filenames where possible. `99-start.js` should own top-level startup and close any wrapper begun in bootstrap, if that pattern is used.

# Testing

Add automated tests using the project’s existing test tooling. If none exists, use Node’s built-in test runner and add a `pnpm test` script. Use pnpm, not npm.

At minimum test:

## Existing compatibility
- Existing standalone script discovery/build still works.
- Existing standalone dispatch still works.
- Existing grouped Gemini build still works.
- Watcher detects edits inside grouped script directories and shared directories.

## Grouping
- Grouped file ordering is exact.
- A declaration in grouped file one is available in grouped file two.
- Two separate grouped scripts do not share lexical state.
- Shared factory code works independently inside two different script wrappers.
- Missing/duplicate/out-of-root grouped paths fail with useful messages.

## Releases
- First build creates a current release.
- Source change creates a second release.
- Identical rebuild does not create a duplicate release.
- Retention pruning obeys configuration.
- Generated bundle contains retained release runners.
- Selecting a retained prior release selects that runner.
- Selecting a missing/pruned release falls back to current and creates a diagnostic warning.

## Runtime gate
- Disabled script does not run.
- Enabled matching script runs.
- Nonmatching script does not run.
- One script failure does not prevent another matching script from running.
- Duplicate-run guard prevents duplicate dispatcher execution in one document.

## Control Center
- Opens through exposed open function/menu-command integration where testable.
- Creates only one root host.
- Toggle writes configuration.
- Release selection writes configuration.
- Invalid imported configuration is rejected safely.
- Valid import merges/normalizes safely.
- No script runs solely because the Control Center is opened on a nonmatching site.

# Build and validation

Run:
- the normal bundle build command
- watcher-related validation if there is a testable command
- syntax validation of the generated bundle
- all automated tests
- any lint/format checks already configured

Then inspect the generated bundle and verify:
- It remains one local `@require` target
- The Control Center runtime is included
- Every script has a stable registry entry
- Gemini appears once as a grouped script entry
- Prior retained script releases are embedded
- No `eval`, `new Function`, dynamic script tags, remote imports, or runtime code fetching were added
- Existing userscripts remain in the output

# Documentation

Update the README with:
- standalone versus grouped script rules
- shared-library rules
- release-history design and retention
- rollback limitations:
  - rollback applies after reload
  - only retained embedded releases are selectable
  - a newly broken bundle can only roll back to versions still embedded in that bundle
  - Git remains the authoritative long-term history
- Control Center shortcut and menu command
- configuration export/import behavior
- instructions for adding a new grouped script
- instructions for adding a genuinely reusable shared factory

Add a concise `docs/architecture.md` showing:
- source layout
- build flow
- generated bundle flow
- registry/release selection flow
- runtime isolation boundaries

# Final report

Return:
1. The inventory summary and which scripts were grouped versus kept standalone
2. Files added/changed/moved
3. The release-history retention policy
4. The Control Center’s capabilities and shortcut
5. Build/test commands run and results
6. Any remaining browser-only manual tests:
   - opening the Control Center on a normal site and on Gemini
   - disabling a script, reloading, confirming it does not run
   - rolling one script back, reloading, confirming the selected release runs
   - confirming a failed script appears in diagnostics without blocking another script
7. Any decisions that require user input before further refactoring

Do not stop at a proposal. Implement the system carefully, preserving current behavior wherever it is not explicitly changed above.
```

One important limitation

An embedded-history rollback protects you **after ordinary source changes**, because the new bundle retains prior script runners. But if the master bundle/control-plane itself is broken, you still need Git or a known-good backup bundle as the escape hatch; keep generated release history in Git and consider retaining timestamped full-bundle copies too. The interface should state this plainly rather than implying it can recover from every class of failure.

---

## User

I thought for version control we WOULD use git. Why wouldn't we use git?

---

## Assistant

## Perplexity — 06:29 PM

Yes—**Git should be the authoritative version control system**. I should clarify: the reason not to use Git was only that a userscript running in Chrome cannot directly execute `git checkout`, inspect branches, or rewrite your working tree. But your **bundler/control service absolutely should use Git**.

The correct design is:


```
text
Control Center UI in browser
        ↓ localhost request
Local userscript-bundler control service
        ↓ git commands + build
Git repository / working tree
        ↓
Rebuilt userscript_bundle.js
        ↓ reload page
Tampermonkey master loader
```

What Git should do

Git provides the real history:

Every modularization or feature change is committed.

Each userscript can have a stable path, so history is naturally per-script:


```
bash
git log -- userscripts/gemini-thread-saver/
```


The Control Center can show commits that changed a specific userscript.

“Rollback Gemini only” can restore the relevant directory from an earlier commit, commit that restoration, rebuild the bundle, then reload.

You retain branches, diffs, blame, tags, remote backup, and unlimited history—unlike a five-release embedded snapshot ring.

For example, the control service can perform a targeted restore:


```
bash
git restore --source <commit> -- userscripts/gemini-thread-saver/
pnpm build
git add userscripts/gemini-thread-saver/ userscript_bundle.js
git commit -m "rollback(gemini-thread-saver): restore <commit>"
```


That changes only Gemini’s sources while leaving other userscripts at their current revisions.

Browser limitation

The browser UI should **request** Git operations; it should not contain Git logic itself.

Your existing architecture already grants the master userscript access to `127.0.0.1`, which makes a local control endpoint practical. The browser Control Center would call a narrowly scoped local service, for example:


```
text
GET  /api/userscripts
GET  /api/userscripts/:id/history
GET  /api/userscripts/:id/diff?from=<commit>&to=HEAD
POST /api/userscripts/:id/restore
POST /api/userscripts/:id/toggle
POST /api/build
```


The local service owns:

Validating script IDs against the manifest

Listing only relevant Git commits

Restoring only allowed directories

Refusing dirty-worktree operations unless explicitly confirmed

Running `pnpm build`

Returning build success/failure and bundle timestamp

Optionally creating an automatic pre-rollback checkpoint commit

Better rollback semantics

There are two sensible operations, and the UI should distinguish them:

Action	What it does	Best use
**Runtime rollback**	Chooses an older embedded script release; reload required	Fast temporary recovery
**Git restore**	Restores source files from a selected commit, rebuilds, commits the restore	Permanent, auditable rollback

The embedded-release mechanism is optional convenience, not version control. It gives you a quick rollback if a newly built bundle still loads, but **Git is the source of truth**.

For your workflow, I would prioritize Git control and possibly omit embedded source snapshots entirely at first. Keep just:

Git history per userscript.

A local authenticated control service.

A cross-site Control Center.

Targeted restore + automatic rebuild.

A known-good bundle backup before every rebuild.

Revised prompt direction

Replace the earlier “release-history and rollback” requirement with this:


```
text
Use Git as the sole authoritative source of version history.

Do not implement source snapshots or embed prior source releases in
userscript_bundle.js as the primary rollback system.

Instead, add a local Userscript Control Service running on 127.0.0.1 that
the Control Center can call through GM_xmlhttpRequest. The service must
provide safe, manifest-scoped Git operations:

- List registered userscripts and current working-tree state
- List commits that changed a selected userscript's source paths
- Show commit metadata and a compact diff/stat for that userscript only
- Restore only the selected userscript's allowed source paths from a
  chosen commit
- Before restoring, create a Git checkpoint commit or require explicit
  confirmation if the working tree is dirty
- Run the normal pnpm bundle command after a successful restore
- Report build status, errors, and generated-bundle timestamp
- Never accept arbitrary shell commands, arbitrary Git arguments, arbitrary
  paths, arbitrary repository URLs, or arbitrary file reads/writes

A rollback must create a new commit such as:
rollback(<script-id>): restore sources from <short-sha>

The browser Control Center must clearly label the two possible operations:
- Temporarily disable a script: affects runtime only after reload
- Restore script from Git commit: modifies local source, rebuilds the bundle,
  creates a new rollback commit, and takes effect after reload

Use Git path history, not whole-repository history, when showing a script:
git log -- <allowed script paths>
```


The ideal end state is: you open `Alt+Shift+U`, find “Gemini Thread Saver,” inspect its own Git history, select the last working commit, click **Restore this script**, confirm, wait for local rebuild success, and reload. That is real version control with a convenient local UI—not a second, weaker history system.

---

## User

yeah we might as well just extend our local server we're using for gemini thread saver to do proper version control rollbacks as triggered by our new embedded interface

---

## Assistant

## Perplexity — 06:29 PM

Yes—that is the cleanest architecture. Extend the existing **Gemini Thread Saver local server on `127.0.0.1:3033`** into a deliberately scoped local “developer control API,” then let the always-available bundled Control Center call it through `GM.xmlHttpRequest`. The Gemini script already uses that localhost service for archive writes and terminal/session actions,

---
