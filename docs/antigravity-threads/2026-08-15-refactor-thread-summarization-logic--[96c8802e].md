---
title: "Refactor Thread Summarization Logic"
date: "2026-08-15"
conversation_id: "96c8802e-9f81-429d-9524-a25fa65aeb02"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

In `/Users/matt/projects/ai-os/scripts/watch_transcripts.py`:

1. In `main()`, pre-populate `summarized_threads` with both `active` and `sub_map` keys:
```python

    active, sub_map = get_active_convs(args.brain_dir)
    last_state = {**active}
    last_render_time = {}
    summarized_threads = set(active.keys()) | set(sub_map.keys())
```

2. In `process_updates()`, fix the idle thread summarization loop so it NEVER summarizes subagents:
```python

    # Summarize idle threads (main threads only, not subagents)
    for conv_id, (mtime, size) in current.items():
        if conv_id not in sub_map and conv_id not in summarized_threads and (now - mtime) > 300:
            summarized_threads.add(conv_id)
            try:
                subprocess.Popen([sys.executable, str(SCRIPTS_DIR / "summarize_thread.py"), conv_id])
            except Exception as e:
                print(f"summarize_thread failed: {e}")
```

</span>



<span title="Responded at 9:18am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

*(response in progress or not recorded)*

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | PPLX Quota |
| :--- | :--- | :--- |
| ~35k / ~400k 🟢 (optimal) | 4:20am | 106 ❓, 16 📤 |

</span>

</span>