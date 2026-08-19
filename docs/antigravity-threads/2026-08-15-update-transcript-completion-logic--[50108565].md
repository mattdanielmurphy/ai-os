---
title: "Update Transcript Completion Logic"
date: "2026-08-15"
conversation_id: "50108565-8661-446e-8d08-882539c4fb78"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">In `/Users/matt/projects/ai-os/scripts/watch_transcripts.py`:

1. Replace `is_in_progress` with `is_turn_completed`:
```python

def is_turn_completed(transcript_path: Path) -> bool:
    """Check if the latest turn in transcript.jsonl has completed (agent stopped calling tools)."""
    if not transcript_path.exists():
        return False
    try:
        with open(transcript_path, 'rb') as f:
            f.seek(0, 2)
            size = f.tell()
            buffer_size = min(size, 8192)
            f.seek(size - buffer_size)
            lines = f.read().decode('utf-8', errors='ignore').strip().split('\n')
            for line in reversed(lines):
                if not line.strip():
                    continue
                obj = json.loads(line)
                t = obj.get('type')
                if t == 'PLANNER_RESPONSE':
                    # Completed turn if no tool calls were made in this planner response
                    return not bool(obj.get('tool_calls'))
                elif t == 'USER_INPUT':
                    # User just asked something, agent hasn't responded yet
                    return False
                else:
                    # Tool execution result -> turn still in progress
                    return False
    except Exception:
        return False
    return False
```

2. In `process_updates` (around line 186):
Update the auto-commit trigger:
```python

            # Auto-commit check (Trigger only once when the entire turn is completed)
            transcript_file = brain_dir / render_id / ".system_generated" / "logs" / "transcript.jsonl"
            if transcript_file.exists() and is_turn_completed(transcript_file):
                workspace_root = Path("/Users/matt/projects/ai-os")
                
                # Check for cooldown per repository
                last_commit_time = last_render_time.get(f"commit_{workspace_root}", 0)
                if (now - last_commit_time) > 10:
                    if has_uncommitted_changes(str(workspace_root)) and str(workspace_root) not in pending_commits:
                        res_path = commit_results_dir / f"{render_id}_{int(now)}.json"
                        proc = subprocess.Popen([sys.executable, str(SCRIPTS_DIR / "auto_commit.py"), "--result-path", str(res_path)])
                        pending_commits[str(workspace_root)] = (proc, res_path, render_id)
                        last_render_time[f"commit_{workspace_root}"] = now
```

Save cleanly and verify syntax.</span>



<span title="Responded at 7:19pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested modifications have been completed and verified.

*   Replaced `is_in_progress` with `is_turn_completed` in `/Users/matt/projects/ai-os/scripts/watch_transcripts.py`.
*   Updated the `process_updates` function to trigger the auto-commit check based on `is_turn_completed(transcript_file)` and adjusted the commit cooldown to 10 seconds.
*   Verified the syntax using `py_compile`.

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota |
| :--- | :--- | :--- | :--- |
| ~35k / ~410k 🟢 (optimal) | 2:20pm | 🟡 Uncommitted (2) | 113 ❓, 19 📤 |

</span>

</span>