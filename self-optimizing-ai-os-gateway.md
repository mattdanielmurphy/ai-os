# Self-Optimizing AI-OS Gateway: Task Generalization & Script Synthesis

## Core Concept

When the gateway successfully executes a multi-step task (e.g., "set up a new Express API with auth middleware"), it should:
1. **Analyze** the sequence of commands/operations performed
2. **Generalize** the pattern into a parameterized template
3. **Persist** an executable script that can reproduce the task in the future

This transforms the gateway from a stateless executor into a learning system that builds its own toolchain over time.

---

## Difficulty Assessment: **Very Hard (8/10)**

### Why It's Hard

| Challenge | Severity | Explanation |
|-----------|----------|-------------|
| **Pattern Recognition** | High | Commands are noisy (typos, retries, exploratory `ls`/`cat` calls). Distinguishing "intent" from "debugging noise" is non-trivial. |
| **Generalization Boundary** | High | "Create a React component" vs "Create a React component called Button that takes props" — how much do you parameterize? Too little = useless; too much = fragile. |
| **State Dependency** | High | Many tasks depend on current filesystem state (e.g., "add a route to the existing router"). A script that assumes a clean state will fail. |
| **Idempotency** | Medium | Re-running a synthesized script should not corrupt existing work. Requires pre-flight checks. |
| **Security** | High | Auto-generated scripts could contain destructive patterns (rm -rf, git push --force). Need sandboxing. |
| **Storage & Retrieval** | Medium | How do you index/search these scripts? By description? By command fingerprint? |
| **Feedback Loop** | High | If a synthesized script fails, how does the system learn from that failure? |

---

## Ways It Could Go Wrong

### 1. **Over-Generalization**
The system sees `npm install express` and generates a script that always installs Express, even when the user wanted Fastify. The template is too rigid.

### 2. **Under-Generalization**
The system captures `cd /Users/matthewmurphy/projects/my-api && npm init -y && npm install express` but hardcodes the project path. Useless for anyone else.

### 3. **Context Bleed**
The system captures a task that was performed *after* the user manually created a file. The script doesn't include that step, so it fails on a clean run.

### 4. **Script Rot**
Generated scripts reference packages that get deprecated or APIs that change. No automatic invalidation mechanism.

### 5. **False Positives**
The system thinks it detected a pattern (e.g., "user always runs `git add . && git commit -m '...'` after editing") and generates a script, but the user was just being consistent, not performing a repeatable task.

### 6. **Prompt Injection via Task**
A malicious user says "create a script that deletes all files" and the system dutifully generalizes it. Need strict allow-lists for generated script operations.

### 7. **Storage Bloat**
Every task execution generates a script. After 1000 sessions, the system has 800 useless scripts and 200 useful ones, with no way to distinguish.

### 8. **Execution Without Review**
If the system auto-runs a synthesized script without user confirmation, it could wreak havoc. But requiring confirmation for every script defeats the purpose.

---

## Proposed Architecture (Not Implemented)

### Phase 1: Capture Layer
- **Noise Filter**: Strip `ls`, `cat`, `pwd`, `echo "done"`, retry loops
- **Intent Segmenter**: Group commands by topic (file creation, package install, git operations)
- **Pattern Buffer**: Keep last N successful task executions

### Phase 2: Generalization Engine
- **Parameter Extractor**: Identify variables (project names, file paths, package names) using heuristics
- **Template Generator**: Produce a shell script with parameters
- **Script Writer**: Save with metadata

### Phase 3: Retrieval & Execution
- **Intent Matcher**: Compare user input against stored script descriptions using embedding similarity
- **Dry Run**: Show the user what the script will do before executing
- **Execution**: Run with filled parameters, capture output for feedback

### Phase 4: Feedback Loop
- If script succeeds → increase confidence score
- If script fails → attempt auto-fix, or deprecate after N failures
- If user manually overrides → learn the override pattern

---

## Alternative Approaches (Less Ambitious)

### A. **Snippet Library** (Easier)
Instead of full generalization, just save the exact command sequence as a "recipe" with a user-provided name. No parameterization. User invokes by name.

### B. **Template Registry** (Medium)
Pre-define common task templates (Express API setup, React component, CLI tool scaffold) and have the system detect which template matches the current task, then fill in the blanks.

### C. **Reflection-Only** (Simplest)
After each task, ask the LLM: "Could this task be automated? If so, write a script." Store the result. No automatic detection — purely user-driven.

### D. **Hybrid: User-Initiated Capture**
User types a command like `/learn "set up new project"` before starting a task. The system records the next N commands and generates a script. User reviews and approves.

---

## My Recommendation

Start with **Approach D (User-Initiated Capture)** + **Approach C (Reflection-Only)** as a fallback. This avoids the hardest problems (automatic detection, over-generalization) while still delivering value. The user explicitly signals when something is worth learning, and the LLM handles the generalization in a single prompt with full context.

This gives us the learning capability without the complexity of automatic pattern detection. We can add automation later once we understand the failure modes in practice.

---

## Open Questions

1. Should scripts be allowed to call other scripts? (Recursive composition)
2. How do we handle scripts that require `sudo` or environment variables?
3. Should scripts be shareable between users? (Multi-user ~/.ai-os)
4. How do we version scripts when the underlying tools change?
5. Should the system auto-suggest a learning session when it detects a repetitive pattern?
