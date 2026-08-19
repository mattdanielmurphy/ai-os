---
title: "Add Watch Mode Script"
date: "2026-08-14"
conversation_id: "73e7c787-e076-4935-b6c5-a3eb1cde856e"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please add `--watch` mode to `/Users/matt/projects/ai-os/scripts/gemini_antigravity_bridge.py`:

1. Add `--watch` flag to `argparse` and `--interval <seconds>` (default 5.0 seconds).
2. If `--watch` is specified:
   - Run an initial sync (or incremental sync using `sync_state.json` cache).
   - Enter a loop sleeping `interval` seconds, scanning `~/Documents/gemini-archive/threads/*.md` for new or modified files (where `md5` differs from `sync_state`), converting them immediately to Antigravity brain threads and updating `thread_summaries.json`.
   - Print clean log messages when a new thread is synced (e.g. `[gemini-bridge] Synced: <title> (<conv_id>)`).
   - Handle KeyboardInterrupt cleanly.

Update `/Users/matt/projects/ai-os/scripts/gemini_antigravity_bridge.py` now.

</span>



<span title="Responded at 12:47am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The updates to `/Users/matt/projects/ai-os/scripts/gemini_antigravity_bridge.py` have been completed.

### Changes implemented:
1.  **Arguments**: Added `--watch` and `--interval` (default 5.0) to the argument parser.
2.  **Logic**: Refactored the synchronization logic into a `perform_sync()` function and wrapped it in a `while True` loop when `--watch` is enabled.
3.  **Logging**: Updated the output message to format: `[gemini-bridge] Synced: <title> (<conv_id>)`.
4.  **Graceful Exit**: Added a `try-except KeyboardInterrupt` block to handle clean shutdowns when running in watch mode.
You can now run the script with:
```bash
python3 /Users/matt/projects/ai-os/scripts/gemini_antigravity_bridge.py --watch --interval 10
```

</span>



</span>

</span>