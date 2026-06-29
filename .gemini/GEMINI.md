<SYSTEM_INSTRUCTIONS>
<AUTO_COMMIT_PROTOCOL>
**Commit:** Generate a technical commit message and run `git add . && git commit -m "[message]"`.
</AUTO_COMMIT_PROTOCOL>

<PROJECT_DETECTION>
1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
3. **Hierarchy:** If no project root is found, default to the current working directory, but NEVER initialize a git repository in `~` or its subdirectories (unless it's a known project folder in `~/projects/`).
</PROJECT_DETECTION>

<CORE_RULES>
1. **Context:** Read `AG_CONTEXT.md` at the project root before ANY work. If missing, create it at the root. Update it with durable knowledge (bullets only) after significant architectural changes.
2. **Safety:** NEVER use `rm`. ALWAYS use `mv [path] ~/.Trash/` (Exception: `node_modules`).
3. **Tooling:** ALWAYS use `pnpm`. NEVER use `npm`.
4. **Privacy:** ALL generated GitHub repos MUST use `--private`.
5. **No Repo in ~:** NEVER initialize a git repository in the home directory (`~`).
6. **Local Temp:** NEVER use system-level `/tmp`. ALWAYS create and use a `./tmp` folder within the current project directory for temporary files or test scripts to avoid permission prompts.
7. **Documentation:** When implementing features or bug fixes, always document any new capabilities, enhancements, or architectural additions by updating the features list in the `FEATURES.md` file at the root of the project.
8. **Token Protection & Builds:** NEVER run raw verbose compile/build commands (like raw `xcodebuild` or raw compiler tasks) that output massive build logs. Always filter command outputs to print only the success status or relevant compiler error/warning highlights (and cap total output size/lines) to prevent blowing out the agent input token context window.

9. **Quiet Run Wrapper:** When running inherently noisy commands (like npm install, pip install, cargo build, etc.), you MUST prefix the command with `qr` to prevent PTY stdout token bloat.
</CORE_RULES>


<TOKEN_MANAGEMENT>
### Token Management
1. Never use `cat` to read files larger than 100 lines. You MUST use `read_lines <file> <start> <end>` or `grep -n` to surgically inspect code surrounding the area you need to edit.
</TOKEN_MANAGEMENT>

<AGENT_WORK_LOGS>
**Instruction:** Maintain a history of agentic attempts across sessions to preserve context.

0. **Fresh Thread Context:** When you receive ANY prompt in a new thread, you MUST immediately check the most recent 2 agent log files in `.agent-logs/` AND do a quick search of the `.agent-logs/` directory for keywords related to the prompt. Use this history to load past context and piece together the knowledge needed to understand the user's intent and execute it correctly.
1. **Log Directory:** ALWAYS look for and maintain an `.agent-logs/` directory at the root of the project.
2. **Reading Logs:** Before starting a bug fix or feature, scan `.agent-logs/` for related past work. Read relevant logs to understand what was tried, what failed, and the architectural context discovered by previous agents. Pay special attention to "What Didn't Work" to avoid repeating mistakes.
3. **Writing Logs & Transcripts:** At the END of every session where you make code changes, you must link the session transcript and write a summary.
   - **Step 1 (Symlink):** Create a symlink of your current brain folder to `.agent-logs/transcripts/<Conversation ID>` using the `Conversation ID` from your user information (e.g., `ln -s ~/.gemini/antigravity-cli/brain/<Conversation ID> .agent-logs/transcripts/<Conversation ID>`).
   - **Step 2 (Summary File):** Create a new log file in `.agent-logs/`.
     - **Naming Convention:** `YYYY-MM-DD_HH-MM_<short-kebab-description>.md`
     - **Required Sections:**
       - `**Transcript**`: A direct markdown link to the symlinked folder (e.g., `[View Full Logs](file:///.../projects/.../.agent-logs/transcripts/<Conversation ID>/)`).
       - `## Goal`: What the user asked for.
       - `## Changes Made`: Files modified, what was changed, and why.
       - `## What Worked`: Confirmed fixes.
       - `## What Didn't Work / Known Issues`: Failed approaches and things that still need attention (crucial for future agents).
       - `## Architecture Notes`: Discoveries about how the codebase works that aren't obvious.
4. **Commit:** Commit the log file alongside your code changes.
</AGENT_WORK_LOGS>

### GLOBAL RULES
- The Deletion Ban: You must never run `rm -rf`. If you need to delete, use `mv [path] ~/.Trash/`.

- Memory Constraint: You must not run raw `git log` commands to dig through history. You MUST use the 2-layer Git pipeline: First call `/Users/matthewmurphy/projects/ai-os/scripts/memory_search.sh <keyword>`, then call `/Users/matthewmurphy/projects/ai-os/scripts/memory_diff.sh <ID>`.

### ANTIGRAVITY (PREMIUM) RULES
- Read Constraint: You are STRICTLY FORBIDDEN from reading full raw code files. To understand codebase structure, you MUST call `/Users/matthewmurphy/projects/ai-os/scripts/ingest_codebase <path>` to get skeletonized ASTs/signatures.

- Write Constraint (Triage Editing System): For precise, simple edits (replacing a string, appending), you MUST use `/Users/matthewmurphy/projects/ai-os/scripts/precision_edit.py` to save tokens. Before making any complex edit or refactor, the agent MUST check the delegation state by running `echo $AIOS_DELEGATE`.
  - Scenario A ($AIOS_DELEGATE is "true"): Use `scripts/mechanical_editor.py` (Quota Saving Mode) for complex logic generation.
  - Scenario B ($AIOS_DELEGATE is "false"): Premium Speed Mode. The agent has full authorization to write the code itself, bypassing `mechanical_editor.py`. However, to prevent bash escaping errors, the agent MUST write the code using a Quoted Heredoc directed into a temporary file, then move it:
    cat << 'EOF_SAFE' > target_file.tmp
    [CODE]
    EOF_SAFE
    mv target_file.tmp target_file
    (The single quotes around 'EOF_SAFE' are absolutely mandatory to prevent shell interpolation errors.)

- TELEMETRY RULE: When you are fully yielding control back to the user at the end of a task, you MUST execute `python /Users/matthewmurphy/projects/ai-os/scripts/get_last_cost.py --agent agy`. You MUST then copy the exact output of that script and append it to the very bottom of your conversational markdown response so it is immediately visible in the UI.

- Context Self-Healing (Automated Subtasking): If a task requires many steps or your context window is bloated, reset your context natively. 
  INDEXED HANDOFF PROTOCOL: To keep the handoff context window small without losing historical data, you must separate summaries from granular details. 
  - Before running `context_handoff.py`, if you have complex logic, command outputs, or nuanced decisions you want to preserve for the next agent, write them to a detail file: `.agent-logs/details/step_<timestamp_or_id>.md`.
  - In the main handoff log under '## Completed So Far', you MUST be extremely succinct. Write only a 1-sentence summary of the achievement, appended with its reference ID. Example: '- [step_171829] Implemented OAuth middleware in auth.py'
  - If you are a newly spawned agent reading a handoff log and you need more context about a specific past step, you can dynamically choose to read its associated `step_<id>.md` file.
  1. Call `/Users/matthewmurphy/projects/ai-os/scripts/context_handoff.py` with your current state.
  2. Read the outputted HANDOFF_FILE_PATH.
  3. Execute a bash command to spawn a fresh child agent: `agy --add-dir=$PWD --dangerously-skip-permissions --prompt "Read the handoff log at [HANDOFF_FILE_PATH] and execute the next steps."`
  4. Wait for the child agent to finish, then report final success to the user.
</SYSTEM_INSTRUCTIONS>
