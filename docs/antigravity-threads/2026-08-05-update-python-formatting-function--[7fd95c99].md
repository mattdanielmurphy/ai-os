---
title: "Update Python Formatting Function"
date: "2026-08-05"
conversation_id: "7fd95c99-fb68-4c60-bd75-48ac61de06c8"
source: "antigravity"
---

# Update Python Formatting Function

## User

In the file `/Users/matt/projects/ai-os/scripts/gen_conversation_md.py`, update the `format_prompt` function to ensure code blocks are cleanly separated by newlines to prevent markdown rendering bleed.

Replace this block:
```python
def format_prompt(raw_prompt: str) -> str:
    """Format a user prompt for display in pure markdown.
    
    No HTML escaping — the content is plain text rendered as markdown.
    Long prompts get wrapped in a <details> collapsible.
    """
    text = raw_prompt.strip()
    lines = text.split('\n')
```

With this block:
```python
def format_prompt(raw_prompt: str) -> str:
    """Format a user prompt for display in pure markdown.
    
    No HTML escaping — the content is plain text rendered as markdown.
    Long prompts get wrapped in a <details> collapsible.
    """
    text = raw_prompt.strip()
    
    # Ensure code blocks are on their own lines to prevent markdown bleed
    text = text.replace('```', '\n```\n')
    import re
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    
    lines = text.split('\n')
```

You must use your file editing tools to apply this change.

---

## Assistant

Created At: 2026-08-05T00:34:10-06:00
Completed At: 2026-08-05T00:34:10-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/ai-os/scripts/gen_conversation_md.py. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -251,6 +251,12 @@
     Long prompts get wrapped in a <details> collapsible.
     """
     text = raw_prompt.strip()
+    
+    # Ensure code blocks are on their own lines to prevent markdown bleed
+    text = text.replace('```', '\n```\n')
+    import re
+    text = re.sub(r'\n{3,}', '\n\n', text).strip()
+    
     lines = text.split('\n')
 
     # Only collapse into <details> if truly massive (> 800 chars or > 12 lines)
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-05T00:34:11-06:00
Completed At: 2026-08-05T00:34:11-06:00
Message sent to "76f4d5f3-0e16-4272-91ad-a3f44dcd9e57".

The `format_prompt` function in `/Users/matt/projects/ai-os/scripts/gen_conversation_md.py` has been updated as requested.

---
