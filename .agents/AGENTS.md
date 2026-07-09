# Personal AI OS - Custom Workspace Rules

## Username & Path Migration Guardrail
- **Context**: The host machine migrated from username `matthewmurphy` to `matt`.
- **Constraint**: When parsing, reading, creating, or writing absolute paths, files, scripts, or configuration settings:
  - ALWAYS translate paths containing `/Users/matthewmurphy/` to `/Users/matt/` (or use relative paths or the active home directory reference `~/` / `std::env::var("HOME")` where appropriate).
  - Pay special attention to symbolic links, environment setups, or hardcoded scripts that may still reference the legacy username and correct them on discovery.

## CSS & Styling Guardrails
- **Constraint**: ALL styles must reside in the central stylesheet (`src/styles.scss`). Never write inline style attributes (`style="..."`) in HTML templates, and never set style properties directly on DOM elements in JavaScript/TypeScript (e.g., `element.style.color = "red"`), unless dynamic layout calculations are absolutely necessary (e.g., dragging window splitters, resizing panel dimensions, or applying dynamic user-selected theme colors). For general UI states, visibility toggles, and formatting, use CSS classes (e.g., `element.classList.toggle('hidden')`) defined in the stylesheet.

## Communication & Interstitial Messages Guardrail
- **Constraint**: NEVER output interstitial status messages, placeholder updates, or intermediate commentary before running commands, launching background tasks, or awaiting compilation/builds (e.g., "I have initiated the build process...", "I will update you as soon as...", "Running the command..."). Simply execute the necessary tools/commands silently or proceed directly without writing text. Only present the final completed results/output when the overall task or step is fully finished.

## macOS Environment Reference
- **Context**: The host machine runs custom Launch Agents, Hammerspoon scripting, and specific helper tools.
- **Constraint**: ALWAYS refer to [MAC_ENVIRONMENT.md](file:///Users/matt/projects/ai-os/docs/MAC_ENVIRONMENT.md) before installing new software, configuring background services/daemons, scripting custom window/system automation, or making system-wide integration decisions.

## Blank Thread / Task Selection Rule
- **Context**: When starting a fresh thread/session (i.e. a "blank thread" where there is no active task with `status: "in-progress"` in `.devtool/features/`):
- **Constraint**: The agent MUST check the existing files in `.devtool/features/*.md` to see if one matches the current user request.
  - **Match Found**: If a matching feature is found, the agent MUST update that file's frontmatter to set `status: "in-progress"`.
  - **No Match Found**: If no matching feature exists, the agent MUST automatically create a new feature file under `.devtool/features/` with:
    - A clean, kebab-case filename (e.g., `some-feature.md`).
    - Frontmatter with `status: "in-progress"`, a unique `id`, `priority: "medium"`, and other metadata fields.
    - A clear, concise title. If it is a bug fix, prefix the title with "Bug: ". For other features, use a regular descriptive title.
    - An improved description of what the user requested in their prompt. Keep it objective and do not editorialize too much.
