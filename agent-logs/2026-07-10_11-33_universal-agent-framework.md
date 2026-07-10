## Goal
Add detailed info to docs and implement the Universal Agent Framework to keep Antigravity IDE, Antigravity CLI (agy), and Claude Code rule configurations in sync.

## User Feedback & Decisions
- Keep settings files physically separate as they contain different, tool-specific keys.
- Add the "context": ["AGENTS.md"] array mapping in both settings files.
- Move workflows to ~/.ai-workflows/ and symlink them for the IDE.
- Use AGENTS.md and CLAUDE.md as the main project rule files.
- Delegate execution to Claude Code (claude-haiku*) to run the changes.

## Changes Made
- Centralized the global workflows (audit.md, fast.md, start.md) into ~/.ai-workflows/ and created symlinks back to ~/.gemini/config/global_workflows/.
- Modified ~/.gemini/settings.json and ~/.gemini/antigravity-cli/settings.json to include "context": ["AGENT[.md"].
- Created /Users/matt/projects/ai-os/AGENTS.md with core rules and global workflow imports.
- Updated /Users/matt/projects/ai-os/CLAUDE.md to reference absolute workflow paths.
- Removed legacy rules file at .gemini/GEMINI.md to prevent race conditions.
- Created task file .devtool/features/universal-agent-framework.md with status set to review.

## What Worked
- Claude 3.5 Haiku successfully executed the updates to both settings.json files, created AGENTS.md, updated CLAUDE.md, and cleaned up legacy GEMINI.md files.
- Staging workflows in a unified location (~/.ai-workflows/) allows both engines to read the exact instructions.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Standalone GEMINI.md / AGENT[.md files do not support frontmatter and are always active for their directory scope.
- Both engines can be pointed to the shared workflows (AGENT[.md) and direct file reading rules (CLAUDE.md).