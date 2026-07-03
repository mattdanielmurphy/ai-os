# CLAUDE CODE - SYSTEM INSTRUCTIONS

## GLOBAL RULES
- The Deletion Ban: You must never run `rm -rf`. If you need to delete, use `mv [path] ~/.Trash/`.
- Memory Constraint: You must not run raw `git log` commands. You MUST use the 2-layer Git pipeline: First call `/Users/matthewmurphy/projects/ai-os/scripts/memory_search.sh <keyword>`, then call `/Users/matthewmurphy/projects/ai-os/scripts/memory_diff.sh <ID>`.
- Write Constraint (Triage Editing System): For precise, simple edits (replacing a string, appending), you MUST use `/Users/matthewmurphy/projects/ai-os/scripts/precision_edit.py` to save tokens. Before making any complex edit or refactor, the agent MUST check the delegation state by running `echo $AIOS_DELEGATE`.
  - Scenario A ($AIOS_DELEGATE is "true"): Use `scripts/mechanical_editor.py` (Quota Saving Mode) for complex logic generation.
  - Scenario B ($AIOS_DELEGATE is "false"): Premium Speed Mode. The agent has full authorization to write the code itself, bypassing `mechanical_editor.py`. However, to prevent bash escaping errors, the agent MUST write the code using a Quoted Heredoc directed into a temporary file, then move it:
    cat << 'EOF_SAFE' > target_file.tmp
    [CODE]
    EOF_SAFE
    mv target_file.tmp target_file
    (The single quotes around 'EOF_SAFE' are absolutely mandatory to prevent shell interpolation errors.)

## CLAUDE-SPECIFIC RULES
- Cost & Quota Telemetry: You MUST run `/Users/matthewmurphy/projects/ai-os/scripts/get_last_cost.py --agent claude` ONLY when you have fully completed a task and are yielding control back to the user. DO NOT run this script during internal tool polling, while waiting for background tasks, or between intermediate steps, as it will cause an infinite loop.

# Human-Centric UI Architecture Rules

## 1. Styling Constraints
- DO NOT use Tailwind CSS, utility-class frameworks, or inline styles.
- Use standard, vanilla CSS via CSS Modules (`*.module.css`).
- Keep presentation layout separate from logic. A human must be able to open the `.css` file and tweak margins, colors, and padding using standard web specifications.

## 2. File Organization & Discoverability
- Every UI component must live in its own dedicated directory named after the component (PascalCase).
- Absolute ban on multi-component files. If a component requires a sub-item (like a list row), spin it out into its own folder.
- File structure must mirror visual hierarchy where practical.

## 3. DOM Tagging for Human Maintenance
- The top-level element of every component must include a descriptive `data-ui` attribute matching the component or feature name (e.g., `data-ui="midi-track-row"`).
- This is a strict requirement to allow human operators to use browser developer tools to inspect an element and instantly map it back to the source file via global search.
