# Agent Work Logs & History

## Agent Work Logs Protocol
0. **Fresh Thread Context & Recent History:** When starting a new thread/session, scan the project root for `AG_CONTEXT.md`, `FEATURES.md`, `DEVELOPMENT_JOURNAL.md`, and `agent-logs/`. Read `DEVELOPMENT_JOURNAL.md` first, then inspect recent logs.
1. **Log Directory:** Maintain `agent-logs/` at the project root.
2. **Reading Logs:** Scan `agent-logs/` for related past work before starting.
3. **Writing Logs:** At the END of every session with code changes, create `agent-logs/YYYY-MM-DD_HH-MM_<description>.md`.
4. **Development Journal:** Append a 2-3 line bullet entry to `DEVELOPMENT_JOURNAL.md` at the project root at the end of every session.
5. **Mandatory Wiki Recording:** Any significant architectural decision, optimization pattern, structural change, or system directive update MUST be recorded in the local LLM Wiki engine (`wiki-engine`) or project context files before concluding the turn.

## Master Project Board Protocol
- **Single Source of Truth**: Active multi-project backlog is maintained in `/Users/matt/projects/ai-os/PROJECT_BOARD.md` (synced with Obsidian `Personal/Development/Project Notes/Global Todos.md`).
- **Hydration & Visibility**: `preflight.py` automatically hydrates in-progress and top backlog items at the start of every session.
- **Surfacing Requirement**: Agents MUST surface the project board with a standard local Markdown link: `[PROJECT_BOARD.md](/Users/matt/projects/ai-os/PROJECT_BOARD.md)`. Do not append editor- or file-manager-specific launcher URLs; the built-in editor handles local file links.
- **Task Schema**: Always format tasks as `- [ ] <description> [project:: <id>] [assignee:: user|agent] [due:: YYYY-MM-DD]`.

# Search-to-Memory & Autonomous Learning Invariant
- **Search Friction as Memory Signal**: Whenever an agent is required to perform exploratory search (e.g. `grep_search`, directory sweeps, config discovery, or web lookups) to resolve an unknown path, hidden setting, architectural dependency, or debugging quirk:
  - The agent MUST NOT discard the discovery upon completing the task.
  - The discovery MUST be immediately persisted to the active memory engine (`~/.hermes/memories/MEMORY.md`, Mem0, or project `AG_CONTEXT.md`) so future sessions bypass exploratory search.
- **Pre-Flight Context Hydration**: Before executing non-trivial architectural, debugging, or workflow tasks, agents must proactively recall relevant context and past lessons rather than operating cold or re-deriving known solutions.
- **Battle-Tested Memory Architecture**: AI-OS memory and self-learning MUST use established, third-party / production memory backends (e.g. Mem0, Hermes FTS5/SQLite engine) rather than ad-hoc homebrew memory scripts.

# Personal Knowledge Base & LLM Wiki Invariant
- **Location**: Matt's personal notes vault and LLM Wiki is located at `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`.
- **Architecture**: Organized per the Karpathy LLM Wiki pattern:
  - `SCHEMA.md`: Domain definition, frontmatter rules, and tag taxonomy.
  - `index.md`: Master catalog of all interlinked notes.
  - `log.md`: Append-only chronological action log.
- **Rule**: Agents MUST NEVER guess or search for alternative wiki directories (e.g. `~/wiki`). All note routing, personal knowledge updates, and wiki operations MUST route directly to this path.
