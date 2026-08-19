---
title: "Update Repository Prompt Instructions"
date: "2026-08-14"
conversation_id: "6568f5cd-6d1d-49fa-a0dc-bc181e98541b"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please update the following files:

1. `/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py`:
Update lines 64-69 so that `repo_info` explicitly instructs Perplexity to use its GitHub connector on the user's private repository:
```python

    if repo_name != "unknown":
        repo_info = (
            f"\n--- GitHub Connector Context ---\n"
            f"Target Private Repository: '{repo_name}'\n"
            f"IMPORTANT: You have access to my authenticated GitHub account via your GitHub connector. "
            f"Please use your GitHub connector to directly read, search, and inspect the codebase, files, and documentation "
            f"in my repository '{repo_name}' (including private files and configs) as needed to construct this plan.\n"
        )
    else:
        repo_info = ""
```

Also in the print instructions (step 2), specify `message` parameter of `proxima:ask_perplexity`.

2. `/Users/matt/.gemini/config/global_workflows/proxima-planner.md`:
Update Step 4 to:
`4. **Invoke Perplexity**: Read the EXACT verbatim text from `./tmp/planner_prompt.txt`. Pass the entire string directly into the `message` parameter of `proxima:ask_perplexity` without summarizing, trimming, or extracting just the user request portion. Ensure Perplexity uses its authenticated GitHub connector to inspect my private repository files and documentation.`

Use `replace_file_content` to make these edits.

</span>



<span title="Responded at 12:49am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Finished updating the files as requested.

</span>



</span>

</span>