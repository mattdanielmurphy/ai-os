---
title: "Update Token Formatting And Polling"
date: "2026-08-15"
conversation_id: "c716e7e4-e67f-4543-8f20-f3a84036e82f"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

You are a leaf file editor. Modify `/Users/matt/projects/ai-os/scripts/postflight_lib.py` and `/Users/matt/projects/ai-os/scripts/watch_transcripts.py`:

1. In `/Users/matt/projects/ai-os/scripts/postflight_lib.py`:
   - Update `format_tokens(tokens: int) -> str`:
     - If `tokens >= 1_000_000`: format as e.g. `1.1M` or `1M`.
     - If `tokens >= 100_000`: round to the nearest 10k (e.g. `219k -> 220k`, `403k -> 400k`).
       Formula: `k_val = round(tokens / 10_000) * 10` -> `f"{k_val}k"`.
     - If `tokens >= 20_000`: round to the nearest 5k (e.g. `23k -> 25k`, `47k -> 45k`).
       Formula: `k_val = round(tokens / 5_000) * 5` -> `f"{k_val}k"`.
     - If `tokens >= 1_000`: round to nearest 1k (e.g. `round(tokens / 1_000)` -> `f"{round(tokens / 1000)}k"`).
     - Otherwise return `str(tokens)`.

2. In `/Users/matt/projects/ai-os/scripts/watch_transcripts.py`:
   - Implement progressive dynamic polling backoff:
     - In the `while True:` daemon loop:
       - Find the latest transcript modification time across active conversations: `newest_mtime = max((mtime for mtime, _ in full_state.values()), default=0)`.
       - Compute `time_since_activity = now - newest_mtime`.
       - If `time_since_activity < 180`: (within 3 minutes of last user/agent message) -> `sleep_interval = 0.05` (50ms ultra-fast responsive polling!).
       - Else if `time_since_activity < 600`: (3 to 10 minutes) -> `sleep_interval = 0.5` (500ms).
       - Else if `time_since_activity < 1800`: (10 to 30 minutes) -> `sleep_interval = 1.5` (1.5s).
       - Else: -> `sleep_interval = 3.0` (3.0s idle resting state).
       - Have `process_updates` return `full_state` or `newest_mtime` so the loop knows the exact activity timestamp, then `time.sleep(sleep_interval)`.

Make these edits now.

</span>



<span title="Responded at 8:59am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested modifications have been implemented:

1.  **`/Users/matt/projects/ai-os/scripts/postflight_lib.py`**:
    *   Updated `format_tokens` with the new tiered rounding logic:
        *   `>= 1,000,000`: Format as `1.1M` or `1M`.
        *   `>= 100,000`: Round to nearest 10k.
        *   `>= 20,000`: Round to nearest 5k.
        *   `>= 1,000`: Round to nearest 1k.
        *   Otherwise: return as is.

2.  **`/Users/matt/projects/ai-os/scripts/watch_transcripts.py`**:
    *   Updated `process_updates` to return the `newest_mtime` from `full_state`.
    *   Modified the daemon `while True` loop to calculate `time_since_activity` and apply progressive polling intervals (50ms, 500ms, 1.5s, or 3.0s).

<details style="margin-top: 8px; font-size: 12px; opacity: 0.75; cursor: pointer;"><summary style="outline: none; cursor: pointer;">✅ <b>Committed</b></summary><div style="padding-top: 4px; font-style: italic;">[`e51ca1a`] Update .agy-mcp/worktrees/job-7f1a74efbfca4784, scripts/postflight_lib.py, wiki-engine</div></details>

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | PPLX Quota |
| :--- | :--- | :--- |
| ~35k / ~400k 🟢 (optimal) | 4:00am | 107 ❓, 16 📤 |

</span>

</span>