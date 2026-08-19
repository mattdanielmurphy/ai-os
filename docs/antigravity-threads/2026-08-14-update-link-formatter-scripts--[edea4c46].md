---
title: "Update Link Formatter Scripts"
date: "2026-08-14"
conversation_id: "edea4c46-6a0f-4e40-9dcd-5fd71860f8db"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Update /Users/matt/projects/ai-os/scripts/link_formatter.py, /Users/matt/projects/ai-os/scripts/postflight_async.py, and /Users/matt/projects/ai-os/tests/test_link_formatter.py:

1. /Users/matt/projects/ai-os/scripts/link_formatter.py:
Make the Zed and Finder action links blank (i.e. `[]({router_zed_url}) []({router_finder_url})`):
```python

        return f'[{label}]({url}) []({router_zed_url}) []({router_finder_url})'
```

Ensure idempotency check checks if `open_zed` or `open_finder` is in `text[end_pos:end_pos + 120]`.

2. /Users/matt/projects/ai-os/scripts/postflight_async.py:
In `run_link_formatter()`:
Check:
```python

def run_link_formatter():
    try:
        from link_formatter import enrich_file_links
        sample = enrich_file_links("[test.md](file:///path/test.md)")
        if "http://127.0.0.1:8643/open_zed" in sample and "http://127.0.0.1:8643/open_finder" in sample:
            return True
        return False
    except Exception:
        return False
```

3. /Users/matt/projects/ai-os/tests/test_link_formatter.py:
Update test assertions to check for `[](http://127.0.0.1:8643/open_zed?path=` and `[](http://127.0.0.1:8643/open_finder?path=`.

Ensure all tests pass.

</span>



<span title="Responded at 1:09am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The updates to the link formatting logic in `link_formatter.py`, `postflight_async.py`, and `test_link_formatter.py` have been completed successfully. All tests, including the updated test assertions, pass as expected.

### Summary of Changes
*   **`link_formatter.py`**:
    *   Changed Zed and Finder links to blank bracket format: `[]({router_zed_url}) []({router_finder_url})`.
    *   Updated the idempotency check to inspect a 120-character buffer after the link, ensuring `open_zed` or `open_finder` presence is correctly detected.
*   **`postflight_async.py`**:
    *   Updated `run_link_formatter()` to reflect the new blank link structure in its diagnostic check.
*   **`test_link_formatter.py`**:
    *   Updated test assertions to verify the presence of `[](http://127.0.0.1:8643/open_zed?path=` and `[](http://127.0.0.1:8643/open_finder?path=`.
I have confirmed that the tests pass:
```bash
python3 -m unittest /Users/matt/projects/ai-os/tests/test_link_formatter.py

### Ran 4 tests in 0.000s

### OK
```

</span>



</span>

</span>