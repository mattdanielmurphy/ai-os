# Handoff: Make ai-os work properly for Claude (assess, tidy, organize, polish)

**Start a new thread with:** "Read ~/projects/ai-os/docs/handoffs/2026-10-17_claude-onboarding.md and continue."
Written 2026-10-17 by Claude (session 1). Everything below was measured or read directly unless marked *(unverified)*.

---

## 1. The goal, in Matt's words and intent

Matt has switched to Claude.app (paid sub) from Gemini/Antigravity/ChatGPT/Codex. He wants to use the switch to **properly assess every part of his local-agent system (`~/projects/ai-os`) as it stands today**:
- decide what works and what doesn't,
- clear out the cruft ("I suspect there's a lot of unnecessary cruft"),
- **surface what fell through the cracks**: unfinished work and ideas with potential,
- tidy, organize and polish, so agents on his Mac work well *for Claude specifically*.

Specific asks he made:
1. **preflight.py**: "a very promising idea, but I wish it were faster and I wish I had more insight into what it's doing, and if it's doing it well."
2. **Shelve `agy`**: the Antigravity trial ended and quota is near zero. Don't forget how to use or hand off to agy; just don't use it now.
3. **Avoid `query_aios`** for now.
4. **Archive without forgetting**: shelved things must stay *visible*. Git branches don't count ("git branches are things I never see"). He dislikes git and resents needing a model to drive it.
5. **Import old threads** (Gemini, Antigravity, ChatGPT, Codex) into Claude.app if possible.
6. **Populate Claude.app's projects list** with his 10 most recently active projects.
7. **Thread-size awareness**: agents should notice when a thread is getting big and urge or create a handoff (like this one) to avoid wasting tokens. He also asked whether Claude.app shows current context size (unanswered; don't guess, verify).

How he likes to work:
- Start with what needs the fewest assumptions; ask about the rest.
- **Ask questions in plain text, not the multiple-choice menu.** It drops quotes and attachments from his answers and covers the thread.
- Flag scope creep and from-scratch projects, but accept them when they're genuinely needed.
- Don't build a custom git GUI. Recommended instead: GitButler (undo timeline, branches shown as lanes) or Fork. He hasn't tried them yet.

---

## 2. Environment facts (save yourself the rediscovery)

- Mac: `matt-local`, arm64, user `matt`. ai-os is at `/Users/matt/projects/ai-os` (git remote `github.com/mattdanielmurphy/ai-os`, branch `main`, about 2,145 commits).
- Claude sessions may run in a **cloud container linked to the Mac**. In that setup `device_bash` is a **Linux VM**, so it cannot run macOS binaries (`osascript`, `ag-quota`, `launchctl`, Hammerspoon). Folders mount at `~/mnt/<name>`.
  - Already granted in session 1: `~/projects`, `~/.gemini`, `~/.codex`, `~/.hermes`. `~/.Trash` was granted but **fails to mount**, so use `ai-os/_to_delete/` instead.
  - `~/Library/Application Support/Claude` is protected and can't be read.
- **Git in the VM needs** `git -c core.fsmonitor=false …`, and `--ignore-submodules=all` on status. Deletion permission in ai-os is needed or git leaves `.lock` files. Commit identity: `Matthew Daniel Murphy <matt@mattmurphy.ca>`. **The VM can't push**; Matt or a Mac-side agent must push.
- **`~/.claude` does not exist on the Mac**: Claude Code CLI is not set up. There are no user-level CLAUDE.md, skills or hooks yet.
- Matt's rule: never `rm`; move things to Trash. `.zshrc_aios` overrides `rm`. Use bun, never npm/pnpm. Repos are `--private`.

---

## 3. Done in session 1 (commits `33f62948`, `e0056f06`; not pushed)

- **PII removed from all agent rule files.** The "Zero-Placeholder Policy" block listed DOB, U of A student ID, ASN, BC PEN, phone and emails. It's replaced with a pointer to **`ai-os/private/identity.md`** (gitignored) in:
  - `.rules/core_safety.md`
  - `CLAUDE.md`, `HERMES.md`, `LEAF.md`
  - `config/codex_policies/policy_personal_ids.md`
  - `~/.gemini/GEMINI.md`, `~/.hermes/HERMES.md`, `~/.codex/policies/policy_personal_ids.md`
  - `compile_dynamic_prompt.py` still finds the block by its "Zero-Placeholder Policy" header.
- **Untracked from git** (files stay on disk): `tmp/`, including a 51 MB `context.md`. It had been tracked despite `.gitignore`. Also 7 `.agy-mcp/worktrees/*` gitlinks plus `tmp/jules_sandbox`, which were broken submodule entries that broke git in the VM.
- **Moved to `ai-os/_to_delete/`** (gitignored, about 4.6 GB): `target/` (Rust build output) and copied browser-history DBs (`tmp/safari_hist.db*`, `chrome_*`, `hist_Profile *.db`, `History*`), plus `tmp/context.md`, `codebase.txt`, `parse_test` and `rules_watcher.log`. **Matt needs to drag `_to_delete` to the Trash.**
- **Not touched**: uncommitted changes in `services/assistant/*` and `Discussions.html`. They're someone else's work in progress.

**Pending decision:** PII is still in **git history** and in about 30 `docs/antigravity-threads/*` files (the admissions and housing threads, plus one gemini thread). Scrubbing history means a rewrite and a force push, which can't be undone. **Ask Matt before doing it.**

---

## 4. What the system is (map)

- **Rules pipeline:**
  - Source: `.rules/*.md` (about 54 KB total).
  - Compiler: `scripts/build_rules.py`, which calls `compile_dynamic_prompt.py`.
  - Outputs: `CLAUDE.md` (28 KB), `HERMES.md` (29 KB) plus `~/.hermes/HERMES.md`, `~/.gemini/GEMINI.md` (`AGENTS.md` is a symlink to it), `~/.codex/AGENTS.md` (minimal), Codex policy packs (`~/.codex/policies`, `config/codex_policies`), and `LEAF.md` (subagents).
  - Outputs are chmod 444. `config/rules_config.json` toggles rules; most of them are gemini_only.
  - `scripts/sync_rules.sh` does a newer-wins sync of GEMINI.md and runs on **every shell start and on every git status/add/commit/diff** via `.zshrc_aios`.
- **Shell layer:** `.zshrc_aios` (via `bin/ai-os` setting `ZDOTDIR`):
  - disables `rm`
  - `qr` quiet-run wrapper around npm/pip/cargo/pytest etc., with logs in `/tmp/aios_last_cmd_*`
  - wraps `git commit` in `qr`
  - **`agy()` is aliased to `scripts/triage_router.py`**
- **`bin/ai-os`** launcher. On every run it:
  - symlinks `~/CLAUDE.md` and `~/MEMORY.md`
  - regenerates a macOS profile (`system_profiler`)
  - regenerates the repo map
  - runs a Hermes thread sync, with a watcher in the background
  - then launches the Tauri GUI (`apps/gemini-companion`), Claude (`--dangerously-skip-permissions`), or agy via `triage_router.py`

  It also references `bin/ai-os-wiki` (Quartz wiki, decommissioned) and `apps/aios-tui` (doesn't exist).
- **Per-turn protocol in the rules:**
  - `preflight.py` at start
  - `postflight.py` before every reply, appending a "Thread Metrics" block (Perplexity quota etc.)
  - `auto_commit.py` (LiteLLM-generated commit messages, secret gate, push)
  - agent logs in `agent-logs/` (414 files) plus `DEVELOPMENT_JOURNAL.md` (65 KB)
  - `PROJECT_BOARD.md`, synced with Obsidian `Personal/Development/Project Notes/Global Todos.md`
- **Memory:**
  - Mem0 via `bin/aios-memory` / `scripts/aios_memory.py`, with Qdrant at `~/.hermes/mem0_qdrant`
  - `~/.hermes/memories/MEMORY.md`
  - Obsidian LLM wiki at `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`
- **Other services:**
  - `services/agy-proxy` (agy)
  - `services/assistant` (Telegram proactive assistant: FSRS reviews, morning nudges; recently active)
  - `services/lecture_mode`
  - `litellm/` (config plus run script, LaunchAgent)
  - `apps/query-aios-companion` (:3031)
- **Scripts:** `scripts/` holds 66 files. About 13 depend on agy/ag-quota (e.g. `handover.py` execs `agy`, `triage_router.py` at 46 KB, `subagent.py`, `swap_turn.py`, `gemini_antigravity_bridge.py`). `query_aios` appears in about 138 files (outside agent-logs).
- **Skills:** 121 dirs under `skills/` (58 MB), mostly Hermes-bundled. Matt's own skills use the `_`-prefix convention (`_plan-with-*`, `_prune-subtractively`, `_critique-without-ghostwriting`…). `scripts/sync_skills.py` copies them to `~/.hermes`, `~/.gemini`, `~/.claude`, `~/.agents`.
- **Docs:** `docs/` is 51 MB:
  - `active/`: VISION.md (29 KB), FEATURES.md (49 KB), best-ideas.md, model-roster.md, universal-agent-framework.md
  - `archive/`
  - `ideas/`: Personalized Prompt Autocomplete, voice/raycast triage, gemini-sonar notes
  - `parking-lot/hermes-inspired-ideas.md`
  - `gemini-threads/` (633 md), `antigravity-threads/` (1,622 md)
  - `memory/`, `handoffs/`
- **Root clutter:**
  - `AG_CONTEXT.md` (24 KB), `HERMES.md`, `LEAF.md`, `FEATURES.md`
  - `README.md`: describes the Tauri GUI and "Triage Mode", which are archived
  - `todo.md`: July Tauri-GUI todos
  - `implementation_plan.md`: belongs to the assistant service
  - `Discussions.html`
  - `test.db` (0 bytes), `.gitignore.bak`
  - `Cargo.toml`/`Cargo.lock` for `crates/aios-core`
  - `.devtool/repo_map.txt` (343 KB)
  - `skills-archive/`, `webui-patches/`, `userscripts/`

---

## 5. Findings and recommendations by area

### 5a. Rules: the most urgent, since they actively misdirect Claude
The compiled `CLAUDE.md` tells Claude to:
- run preflight, postflight and auto_commit **every turn**
- hand off via `handover.py` (which `execvp`s `agy`)
- "Exclusively use agy for subagents"
- follow the query_aios policy and the "escalate to Gemini Flash via agymcp" rule
- format every reply as `<details>`/`<summary>` HTML with span-only styling and `<br>` spacing
- reference Perplexity quota

Much of the rule set exists to manage weaker or cheaper models and Antigravity quirks: token-waste rules, three-turn delegation, orchestrator-only mode, flash_lite delegation.

**Recommendation:**
1. Create a lean user-level `~/.claude/CLAUDE.md` (target a few KB) holding only durable preferences:
   - safety (Trash, not rm)
   - bun
   - private repos
   - project dir conventions
   - always test
   - puma-dev `.test` domains
   - VPS database
   - Apple Reminders for personal to-dos
   - Apple Music link rule
   - wiki path
   - the anti-scope-creep guardrail
   - the secret-isolation rules
   - the identity pointer
2. Move agy/query_aios/Perplexity/escalation/HTML-formatting/handover rules to the shelf (see 5d). Keep them out of the compiled output.
3. Decide whether postflight's "Thread Metrics" block still makes sense; it reports Perplexity quota, which has been removed.
4. Consider replacing "MUST run preflight" text with a Claude Code **SessionStart hook** once Claude Code is installed on the Mac *(verify hook behaviour in current docs first)*.
5. Look at `.rules/proposals/` (6 synthesis files) before deciding anything.

### 5b. preflight.py (`scripts/preflight.py`, 514 lines)
**What it does on the first turn:**
- **Context (main thread):**
  - lists recent threads (from Antigravity brain dirs)
  - shows the project board (In Progress + top backlog)
  - hydrates Mem0 memories
- **Checks (parallel steps):**
  - ag-quota
  - AI-OS planner ping (:3031)
  - rules rebuild-if-stale
  - secret audit of the staged diff
  - git pull (skipped if the tree is dirty; warns at more than 10 changes)
  - transcript watcher (starts the daemon or loads the LaunchAgent)
  - Hammerspoon console errors (osascript)

On later turns it runs only quota and secret audit.

**Measured (`tmp/last_preflight.log`, 377 runs, Jul 28 – Oct 17):**
- Median 3s, p90 6s, max 69s.
- **These understate the real time**: `get_thread_context()` runs *before* `log_preflight("STARTED")`.

**Problems found:**
1. **Stale context:** it only reads `~/.gemini/{antigravity-ide,antigravity,antigravity-cli}/brain/` (2,371 + 1,147 + 139 dirs). The newest is from **Sep 10**, so it shows month-old Antigravity threads. It stats about 3,650 dirs, then fully reads and regex-scans up to 30 transcripts (about **16.5 MB** for the newest 30 per dir) for titles and folders.
2. **Dead checks:**
   - `step_quota`: `ag-quota`, 5s timeout, trial over
   - `step_aios_planner`: :3031, query_aios paused
3. **Slow checks:**
   - `aios-memory preflight` (6s timeout; 15-minute cache in `~/.hermes/cache`)
   - `git pull` (5s)
   - osascript to Hammerspoon
4. **Reports OK on failure:**
   - `step_secret_audit` returns `"Secret Audit: OK (<exception>)"` when it crashes
   - `step_bloat` returns OK on a non-zero exit
   - `step_bloat` is defined but not even in the step list
5. **Side effects:** the watcher step can launch daemons. `step_rules` can rebuild rules.
6. **No insight:** the log is just `STARTED`/`COMPLETED` lines to `~/.preflight.log` and `./tmp/last_preflight.log`. There are no per-step timings or results.
7. **Hardcoded paths** to `/Users/matt/...` throughout. It uses `glob`, `re` and `urllib`, with no external dependencies.

**Recommendation (v2):** keep the concept and the output shape agents rely on.
- Log one JSONL line per step: name, ms, status (OK/WARN/FAIL/SKIP), reason.
- Start the timer at process start.
- Add `preflight.py report`: last N runs, slowest steps, failure rates. Optionally a tiny HTML view.
- Drop the quota and planner steps; shelve them with agy.
- Recent-thread context from a **single source that reflects current tools** (Claude's own history when available, or the thread archive index from 5e). Don't read transcripts.
- Statuses must be honest. Side-effect steps go behind a flag.
- Target under 1s. Keep `tests/test_preflight.py` passing and extend it.
- It can't be timed from the Linux VM because the osascript/ag-quota steps need macOS, so run it on the Mac.

### 5c. Cleanup candidates (propose a list to Matt, then act; move, don't delete)
- `_to_delete/`: Matt empties it.
- 9 local `agy-mcp/job-*` branches, plus remote `agy-mcp/job-7f1a…`, `codex/agy-default-medium`, `jules-*`, `fix-openrouter-hardcoded-key-*`. Also `archive/custom-tauri`, `archive/macos-app`, `old`, `main-before-chatgpt`. Shelf candidates: record them in a shelf README before deleting anything.
- `.agy-mcp/worktrees/` on disk (9 worktrees).
- `tmp/` (still 24 MB of one-off scripts: tailwind cleaners, `edit*.py`, planner outputs, `asar_extracted`, `news_cache`, `subagent_logs`).
- `litellm/config.yaml.bak-2026-08-10`, `.gitignore.bak`, `test.db`, `scripts/.sync_skills_state.json` (89 KB).
- `README.md` and `todo.md`: rewrite or shelve; both describe the dead Tauri GUI.
- `bin/ai-os`: dead `wiki` and `--tui` options. Per-launch profiling plus repo-map regeneration is slow and not needed.
- `.zshrc_aios`: rules sync on every git command, plus the `agy()` alias to triage_router.
- `.devtool/repo_map.txt` (343 KB) and `scripts/generate_repo_map.py`: are they still used?
- Hermes-bundled skills (most of the 121) vs Matt's `_` skills: keep his own, shelve or ignore the bundled ones.

### 5d. The "shelf" (visible archive)
**Proposal:**
- Top-level `ai-os/shelf/<name>/` with a `README.md` per item: what it was, why it's shelved (date), what depended on it, exact steps to revive.
- Nothing in `shelf/` is compiled into rules or run by preflight.
- First residents:
  - `agy` (agy rules, agy-mcp, handover.py, triage_router, agy-proxy, ag-quota steps)
  - `query_aios` (scripts/query_aios.js, query-aios-companion, planner rules)
  - Perplexity bits
  - Tauri GUI docs
- Optionally a `shelf/INDEX.md` table, and a git tag per shelving for exact restore.

Confirm the layout with Matt before moving lots of files; `scripts/` paths are hardcoded in many places.

### 5e. Thread import and archive (what Matt actually gets)
- **Claude.app cannot import other apps' conversations as Claude chats** (no API). So, make old threads *searchable from Claude* instead.
- **Current stores:**
  - Hermes `~/.hermes/state.db` (about 700 MB; tables `sessions`, `messages`, FTS5 + trigram). 3,403 sessions, sources: `gemini-archive` 2,261, `antigravity-app` 557, `antigravity-cli` 408, `webui` 52, `acp` 45, `tool` 27, `cli`/`desktop` 15 each, `subagent` 12, others.
  - Codex: 19 session jsonl files under `~/.codex/sessions` and `archived_sessions`, plus `session_index.jsonl`.
  - Antigravity raw: brain dirs above.
  - ai-os markdown exports: `docs/gemini-threads` (633), `docs/antigravity-threads` (1,622).
  - ChatGPT: **no local data found**. Matt must request a data export from ChatGPT settings.
- **Matt's concern:** Hermes was an experiment, and he's not sure it makes sense to keep relying on its DB, since its schema could change.

  **Agreed direction:** plain markdown files (one per thread) are the durable archive. A small search index is disposable and can always be rebuilt from them. Export anything only Hermes holds, plus Codex and the ChatGPT export, into that format. Expose search and read to Claude through a small read-only local connector. Then shelve Hermes.

  Existing pieces to reuse: `scripts/gen_conversation_md.py` (36 KB, has tests), `ingest_gemini_archives.py`, `ingest_antigravity_sessions.py`, `export_recent_threads.py`, `recent_threads.py`, `sync_threads.py`.

  Hermes ships `hermes mcp serve` (`projects/hermes-agent/mcp_serve.py`), but it's a messaging and channels bridge, not full-text search.
- **Separately:** ChatGPT and Gemini *saved memories* can be brought into Claude's memory with Claude's memory-import feature.

### 5f. Claude.app projects list
- There's no API and Claude's app data is protected. The options are a one-time manual setup, or Claude creating them by driving the app (computer use). **Still unclear which list Matt means** (sidebar Projects vs folder recents for coding); ask in plain text.
- Top 10 by last commit (Oct 17): ai-os, qwerty-midi-plugin, daily-mini-crossword, chrome-devtools-mcp-lazy, mattmurphy.ca, qwerty-midi-hammerspoon, ps5-controller-hammerspoon, userscript-bundler, agy-mcp (shelved, so suggest hermes-agent or imessage-voice-memo instead), karabiner-chatgpt-dictation.

### 5g. Thread-size awareness and handoffs
- **Wanted:** agents notice big threads, nudge Matt, and write a handoff file (`docs/handoffs/YYYY-MM-DD_<topic>.md`, like this one) that a fresh thread can pick up.
- **Options:**
  - a Claude "mod" (plugin) that shows context size in the status line and nudges at a threshold *(unverified whether a mod can read context size)*
  - a `/handoff` skill or command
  - a rule in the lean CLAUDE.md
- The old system had `scripts/handover.py`, `context_handoff.py`, `check_thread_bloat.py` and `thread_economics.py`. Mine them for ideas and shelve the agy-specific parts.
- Verify in current docs whether Claude.app shows context usage. The terminal version of Claude Code has `/context`.

### 5h. Things that fell through the cracks (surface these to Matt as a short list)
- **PROJECT_BOARD backlog:**
  - Mem0 migration of the Obsidian wiki (marked HIGH)
  - harvest insights from thread history into memory (HIGH)
  - gemini-thread-sync userscript fix (In Progress since ~Sep)
  - QWERTY HUD blur
  - unified Thread Browser
  - Hermes WebUI fork
  - clipboard history app
  - Perplexity sync userscript
  - Bartender replacement
  - Apple Music library/playlist automation (due Sep 29, overdue)
- **`docs/ideas/`:** personalized prompt autocomplete, voice/raycast triage architecture, gemini-sonar orchestration.
- **`docs/parking-lot/hermes-inspired-ideas.md`**, `docs/active/best-ideas.md`, `VISION.md`, `universal-agent-framework.md`, `cache-aware-thread-handoff-and-fail-gate.md`, `cross-platform-prompt-history-sync.md`.
- **README roadmap items:** VSCode extension, tree-sitter ingestion, auth rotation daemon, semantic thought layer.

Read these files (not done in session 1) and give Matt a ranked "worth reviving / shelve / drop" list. Several are tied to agy, Hermes or the Tauri GUI and should probably be shelved with them.

---

## 6. Suggested order for the next thread
1. Quick confirmations with Matt (plain text, one message): history scrub yes/no; shelf layout OK; which "projects list"; cleanup-list approval style.
2. **Rules rewrite**: lean `~/.claude/CLAUDE.md`, shelve agy/query_aios rules, rebuild outputs, and make sure Gemini/Codex outputs still build.
3. **preflight v2**, with timing, report and tests.
4. **Shelf + cleanup** (from an approved list), then rewrite README.md as a current map of the system.
5. **Thread archive**: plain files, index, connector, shelve Hermes.
6. Thread-size awareness and handoff tooling.
7. Fell-through-the-cracks review list for Matt.
8. Claude.app projects (once clarified).

Keep commits small and descriptive. Remind Matt to push, or push from a Mac-side session.
