# Gateway Living Rulebook

## Permanent Preferences
- **System OS:** macOS
- **Package Manager:** `pnpm` exclusively (NEVER use `npm` or `yarn`).
- **Repositories:** All generated GitHub repos MUST be configured with `--private`.

## Development Constraints
- **File Deletion:** Never use `rm`. All operations route to macOS `~/.Trash/` via the Gateway sandbox.
- **Root Restrictions:** No repositories initialized in the `~` home directory.
- **Temporary Files:** Use local project `./tmp` directory for all sandbox runs, NOT system-level `/tmp`.
- **Logs:** Verbose compiler logs must be intercepted and stripped; only successes or hard errors are passed to context.
- **Directory Consideration & Nesting:** When asked to create new tools, files, or utilities, if the active directory is a generic parent folder (e.g. `~/projects`), do not write files directly there. Create a dedicated subfolder for the target project/utility, and place all files/subdirectories inside it.

## Style Configurations
- Favor deterministic ES Modules (`type: "module"`) over CommonJS for Node.js scripts.
- Prefer asynchronous `fs.promises` or localized `execSync` for pure OS-level file extractions where appropriate.

## Pre-Flight Critique
Before executing a file change or terminal command, the execution layer must explicitly run through this internal critique loop:
1. "Did I interpret the user's implicit intent, or did I blindly map their words to a literal command?" (e.g., If they say 'projects', are they tracking directories or active code codebases?)
2. "What are the edge cases of the code layout I am about to run?"
3. "Does this choice match the explicit rules listed in the current project rulebook.md?"
4. "Quantity and Granularity: Did the user ask for a list/plurality (summary/metadata) or a specific item/singular (full content)? Avoid dumping large file contents unless explicitly requested or implied by a singular 'the most recent' query."

- Never pass unescaped exclamation marks ('!') in shell commands to avoid history expansion errors; use file-editing tools instead or escape the character.
- All new projects must default to folders under /Users/matthewmurphy/projects/
- When identifying the 'most recent X' (singular, e.g., note, file, document) for a user, refine the search to target the most recently modified *non-hidden, non-system file* and proactively display its human-readable content.
- When identifying 'most recent Xs' (plural, e.g., notes, files), provide a concise list of the top 5-10 most recent items with their modification dates and paths, rather than displaying the full content of any single file.
- **Personal Notes Definition:** When the user refers to "notes" or "my notes", this EXCLUSIVELY refers to personal documents within the Obsidian vault path specified in AG_CONTEXT. Never return agent logs, system logs, or temporary scratchpad files when "notes" are requested.
- **Tool Priority:** If a user explicitly requests a specific tool (e.g., "using the write_file tool"), you MUST prioritize that tool over direct workspace metadata queries.
- **Scope Limitation:** If a request is unrelated to software development, system configuration, or file manipulation (e.g., jokes, general history), state that it is outside the gateway's primary scope before providing a brief, concise response.
- **Saving to User Notes:** When asked to "save to notes", interpret "this" as the relevant content/history. Generate a descriptive filename (e.g., `Note_YYYY-MM-DD.md`), save to the Obsidian path in AG_CONTEXT, and confirm with a markdown link.
- When listing 'notes' (e.g., 'most recent notes'), explicitly filter for actual note file extensions (e.g., `.md`) and exclude hidden system files (e.g., `.DS_Store`, `.git` artifacts) by default. Additionally, prefer `perl -MPOSIX -pe` with `strftime` for robust Unix timestamp to human-readable date conversions in shell commands, especially when file paths might contain spaces.
