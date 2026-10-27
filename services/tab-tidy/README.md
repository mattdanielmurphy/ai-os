# Tab Tidy

Keeps Chrome's tab pile small. Every 2 hours (or when you click its toolbar icon) it:

1. **Closes stale tabs**, after writing each one to `~/projects/ai-os/private/tab-tidy/closed.md` (title + link, so nothing is lost).
2. **Groups the rest** by the day you last used them and their topic: `Today · School`, `Yesterday · Shopping`, `Mon · Music`, `Older · Dev`. Oldest groups at the top, newest at the bottom; groups older than yesterday are collapsed.

## What it never touches

- **Tabs in your own groups.** Put a tab in any group whose name doesn't start with a day (e.g. "Read later") and it's safe forever.
- Pinned tabs, tabs playing sound, and the tab you're looking at.

## When a tab closes

| Tab | Closes after | Haiku can save it? |
|---|---|---|
| Empty New Tab page | 1 h unused | no |
| Duplicate of another open tab | 1 h unused | no |
| YouTube | 6 h unused | no |
| Everything else | 24 h unused | yes |
| Heavy site still in memory (Figma, Docs, Maps, social feeds…) | half the time (12 h) | yes |
| Site you've visited 3 times or fewer | 3× longer (72 h) | yes |

"Haiku can save it" means Haiku looks at the title and keeps anything specific and hard to find again (a listing you're comparing, a forum thread, an order page, a half-done form). If Haiku is unavailable, only the "no" rows close.

All numbers are knobs in the ⌃⌥⌘T Tweaks panel (`~/.hammerspoon/tweaks/tab_tidy.json`), including `dry_run` (1 = only list what would close in `dry-run.md`).

## Setup (once)

1. `./install.sh` registers the helper with Chrome.
2. In Chrome: `chrome://extensions` → turn on Developer mode → Load unpacked → pick `services/tab-tidy/extension`.

Haiku runs through the `claude` CLI (your Claude subscription, no API key).

## Files

- `extension/`: the Chrome extension (reads tabs, applies closes and groups).
- `host/tab_tidy_host.py`: the native helper (rules, Haiku, archive). Tests: `python3 host/test_tab_tidy.py`.
