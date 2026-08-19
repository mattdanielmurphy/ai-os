---
title: "Execute the Pro 3.1 technical plan to fix /planner skill registration across Antigravity.app and agy CLI:"
date: "2026-07-29"
conversation_id: "5cf219c8-6c7f-4fc3-97d5-fc2b3cb4a008"
source: "antigravity"
---

# Execute the Pro 3.1 technical plan to fix /planner skill registration across Antigravity.app and agy CLI:

## User

Execute the Pro 3.1 technical plan to fix /planner skill registration across Antigravity.app and agy CLI:

1. Edit `/Users/matt/projects/ai-os/scripts/sync_skills.py`:
   - Change `HOME / ".antigravity" / "skills",` (line 32) to `HOME / ".gemini" / "antigravity" / "skills",`

2. Edit `/Users/matt/projects/ai-os/scripts/triage_router.py` (if it exists):
   - Locate `force_cli` check around line 570 and make sure prompt starting with '/' forces CLI execution (`or query.startswith("/")`).

3. Execute `python3 /Users/matt/projects/ai-os/scripts/build_rules.py` to run the updated sync_skills script.

Do all edits directly using your write tools.

---
