---
name: fast
description: Respond to the user's next prompt under a strict efficiency constraint, bypassing multi-step planning and returning only the direct output or code diff.
---
1. Analyze the user's next prompt under a strict efficiency constraint.
2. Completely bypass multi-step internal planning, task lists, and file structure mapping.
3. Move straight to outputting the code diff or direct text response.
4. If the request is a trivial change, return *only* the modified code block—absolutely no conversational filler or summaries.
