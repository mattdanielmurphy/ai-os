---
title: "Create SmartSelector Documentation File"
date: "2026-08-05"
conversation_id: "b288c0e5-2dab-4b92-96ae-ce47b4dcc11e"
source: "antigravity"
---

# Create SmartSelector Documentation File

## User

Create a new file at `/Users/matt/projects/userscript-bundler/docs/smart-selector-idea.md` with the following exact content:

```markdown
# Idea: SmartSelector — Resilient DOM Element Cache

> Inspired by a caching pattern from a Hammerspoon AX-element hotkey:
> cache the element ref, validate on use, fall back to re-search if stale.

## The Core Pattern

Instead of calling `document.querySelector()` on every action, cache the
element reference and validate it cheaply with `isConnected` before use.
Only run the full selector search on a cache miss.

```js
let _cache = null;

function getButton() {
  if (_cache?.isConnected) return _cache;          // fast path (~0ms)
  _cache = document.querySelector('.send-btn');    // slow path, re-cache
  return _cache;
}
```

## Why Userscripts Need More Than This

Unlike a desktop AX tree (which only breaks on window close/reopen), the
browser DOM breaks refs in several additional ways:

| Problem | Cause | Frequency |
|---|---|---|
| Element ref stale | React/Vue swapped the node | Very common in SPAs |
| Selector itself rots | Site deploy renames classes (`send-btn` → `x7f2a`) | Occasional |
| Element not yet present | Lazy-loaded / async content | Common |
| Soft navigation | SPA route change, no `DOMContentLoaded` | Common |

## Proposed: `SmartSelector` Utility Class

A drop-in utility you import into any userscript:

```js
const sendBtn = SmartSelector.from([
  { css: '[aria-label="Send message"]' },   // most stable (ARIA)
  { text: 'Send message', role: 'button' }, // text content fallback
  { css: 'form button[type=submit]:last-child' }, // structural fallback
]);

sendBtn.click(); // cache + fallback + re-search handled transparently
```

### Design

```
┌─────────────────────────────────────────────────────┐
│                  SelectorStrategy                    │
│  Priority list of finders, tried in order on miss:  │
│  1. CS
<truncated 828 bytes>
───────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│                  MutationObserver                    │
│  Watches document.body for subtree changes;         │
│  debounces invalidate() to avoid SPA thrashing      │
└─────────────────────────────────────────────────────┘
```

### Key Implementation Notes

- **`isConnected`** is the DOM equivalent of `pcall(performAction)` —
  synchronous, reliable, no exceptions.
- **Selector priority matters** — ARIA attributes and text content are far
  more stable across deploys than minified class names. Put them first.
- **Debounce `MutationObserver`** — busy SPAs fire hundreds of mutations/sec.
  Don't null the cache on every React state tick. Use a ~200ms debounce.
- **Hook `history.pushState`** (or the Navigation API) to hard-invalidate
  on soft navigations, not just DOM mutations.
- **Lazy-load guard** — if all strategies return null, set up a one-shot
  `MutationObserver` to retry when new nodes appear, then resolve a Promise.

## Fit with This Project

This could live as a shared utility in the userscript bundler's runtime
preamble — injected once, available to all scripts as `window.__SS` or via
the module system. Scripts declare their selectors at the top; the bundler
could even lint for raw `querySelector` calls and suggest SmartSelector.

## Status

- [ ] Prototype `SmartSelector` class
- [ ] Integrate with bundler runtime preamble
- [ ] Add linting rule for raw `querySelector` in userscript source
```

Use `write_to_file` with `Overwrite: false`.

---

## Assistant

Created At: 2026-08-05T04:23:10-06:00
Completed At: 2026-08-05T04:23:10-06:00
Created file file:///Users/matt/projects/userscript-bundler/docs/smart-selector-idea.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T04:23:11-06:00
Completed At: 2026-08-05T04:23:11-06:00
Message sent to "87630d27-d058-4309-9839-1c461c82a15a".

OK. The file `/Users/matt/projects/userscript-bundler/docs/smart-selector-idea.md` has been created with the specified content.

---
