---
title: "Refactor Commit Assignment Logic"
date: "2026-08-15"
conversation_id: "15102816-4669-477e-8d96-ec2be46b21e5"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">In `/Users/matt/projects/ai-os/scripts/gen_conversation_md.py`, in `generate()`, place the commit assignment logic BEFORE the `reversed_exchanges` loop:

```python

    # Map commit results to completed exchanges
    commit_dir = app_data_dir / 'brain' / '.commit_results'
    commit_results = []
    if commit_dir.exists():
        for r in commit_dir.glob(f"{conv_id}_*.json"):
            try:
                res = json.loads(r.read_text())
                if res.get("status") == "committed" and res.get("sha"):
                    commit_results.append((r.stat().st_mtime, res))
            except:
                continue
    commit_results.sort(key=lambda x: x[0])

    # Assign commits to completed exchanges
    exchange_commits = {}
    completed_indices = [idx for idx, ex in enumerate(exchanges) if ex.get('type') == 'exchange' and not ex.get('is_in_progress')]
    for commit_time, res in commit_results:
        if completed_indices:
            best_idx = completed_indices[-1]
            exchange_commits[best_idx] = res

    reversed_exchanges = list(reversed(exchanges))
    for i, item in enumerate(reversed_exchanges):
        if item['type'] == 'exchange':
            orig_idx = len(exchanges) - 1 - i
            agent_content = item.get('agent_content', '').strip()
            # Drop empty historical exchanges (only newest exchange i==0 can be in-progress)
            if not agent_content and i > 0:
                continue

            agent_content = clean_agent_content(agent_content)

            # Attach commit badge only if this exchange is completed and has a commit
            if orig_idx in exchange_commits and not item.get('is_in_progress'):
                res = exchange_commits[orig_idx]
                commit_badge = f'\n\n<details style="margin-top: 8px; font-size: 12px; opacity: 0.75; cursor: pointer;"><summary style="outline: none; cursor: pointer;">✅ <b>Committed</b></summary><div style="padding-top: 4px; font-style: italic;">[`{res["sha"][:7]}`] {res["message"]}</div></details>\n'
                agent_content += commit_badge

            # Check for subagent progress
            progress = None
            if i == 0:
                progress = get_subagent_progress(conv_id, app_data_dir)

            block = make_exchange_block_with_progress(item['users'], agent_content, item['agent_time'], progress, i == 0)

            # Prepend banner to the first exchange block
            if i == len(reversed_exchanges) - 1:
                block = f"{banner}\n\n{block}"

            doc_content.append(block)
        elif item['type'] == 'fork_notice':
            doc_content.append(make_fork_notice_block(item['fork_path'], item['undone_count']))
```</span>



<span title="Responded at 9:25am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The commit assignment logic in `/Users/matt/projects/ai-os/scripts/gen_conversation_md.py` has been updated as requested. It now correctly maps commits to completed exchanges *before* iterating through the exchanges for rendering.

<details style="margin-top: 8px; font-size: 12px; opacity: 0.75; cursor: pointer;"><summary style="outline: none; cursor: pointer;">✅ <b>Committed</b></summary><div style="padding-top: 4px; font-style: italic;">[`fd56f70`] Update .agy-mcp/worktrees/job-7f1a74efbfca4784, Discussions.html, scripts/__pycache__/gen_conversation_md.cpython-314.pyc and 3 other file(s)</div></details>

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | PPLX Quota |
| :--- | :--- | :--- |
| ~35k / ~400k 🟢 (optimal) | 4:25am | 106 ❓, 16 📤 |

</span>

</span>