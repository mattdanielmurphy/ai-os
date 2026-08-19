---
title: "Update Git Commit Integration"
date: "2026-08-15"
conversation_id: "37967762-549c-4dbf-a558-57bb0012e9d8"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">Please update the following files in /Users/matt/projects/ai-os:

1. `/Users/matt/projects/ai-os/scripts/postflight_lib.py`:
- Add `get_git_commit_status(repo_root: str = "/Users/matt/projects/ai-os") -> dict`:
```python

def get_git_commit_status(repo_root: str = "/Users/matt/projects/ai-os") -> dict:
    import subprocess
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return {"state": "error", "badge": "🔴 Error", "count": 0}
        
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        if not lines:
            return {"state": "clean", "badge": "🟢 Clean", "count": 0}
        
        for l in lines:
            if l.startswith("UU") or l.startswith("AA") or l.startswith("UD") or l.startswith("DU"):
                return {"state": "error", "badge": "🔴 Conflict", "count": len(lines)}
        
        return {"state": "uncommitted", "badge": f"🟡 Uncommitted ({len(lines)})", "count": len(lines)}
    except Exception:
        return {"state": "error", "badge": "🔴 Error", "count": 0}
```

- In `compute_thread_metrics(conv_id: str = None, agent: str = "antigravity", workspace_root: str = "/Users/matt/projects/ai-os") -> dict`:
  Compute `commit_status = get_git_commit_status(workspace_root)` and include `"commit_status": commit_status` in the returned dictionary.
- In `format_metrics_table(metrics: dict, conv_id: str = None) -> str`:
  Update headers to `["Tokens", "Expiry", "Committed"]`.
  Extract `commit_badge = metrics.get('commit_status', {}).get('badge', '🟢 Clean') if isinstance(metrics.get('commit_status'), dict) else '🟢 Clean'`.
  Append `commit_badge` as the 3rd value in `values`.
  Keep `"PPLX Quota"` if present as the 4th column.

2. `/Users/matt/projects/ai-os/scripts/gen_conversation_md.py`:
- Remove the `.commit_results` directory scanning logic (lines 654-674):
```python

    # Map commit results to specific exchanges by timestamp window
    commit_dir = app_data_dir / 'brain' / '.commit_results'
...
```

- Remove the inline commit badge insertion logic on agent content (lines 686-691):
```python

            # Attach commit badge only if this exchange is completed and has a commit
            if orig_idx in exchange_commits and not item.get('is_in_progress'):
                res = exchange_commits[orig_idx]
                commit_badge = f'\n\n<details style="margin-top: 8px; font-size: 12px; opacity: 0.75; cursor: pointer;"><summary style="outline: none; cursor: pointer;">✅ <b>Committed</b></summary><div style="padding-top: 4px; font-style: italic;">[`{res["sha"][:7]}`] {res["message"]}</div></details>\n'
                agent_content += commit_badge
```

Make sure the files are saved cleanly and accurately.</span>



<span title="Responded at 6:49pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

All requested updates have been completed successfully:

### `/Users/matt/projects/ai-os/scripts/postflight_lib.py`
- Added `get_git_commit_status()` function.
- Integrated `get_git_commit_status` into `compute_thread_metrics()`.
- Updated `format_metrics_table()` to include the new "Committed" column in the thread metrics table.

### `/Users/matt/projects/ai-os/scripts/gen_conversation_md.py`
- Removed the deprecated `.commit_results` directory scanning logic.
- Removed the inline commit badge injection from agent content.

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | PPLX Quota |
| :--- | :--- | :--- |
| ~40k / ~410k 🟢 (optimal) | 1:50pm | 113 ❓, 19 📤 |

</span>

</span>