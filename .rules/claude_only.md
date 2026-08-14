## Claude Code / Hermes Agent Specific Rules

## Mandatory Post-Flight Response Protocol
- **Rule:** Before concluding any turn or delivering a final response to the user, the agent MUST execute `python3 /Users/matt/projects/ai-os/scripts/postflight.py` (or pipe the response through it) to obtain live thread metrics and quota information (token count, Perplexity quota, etc.), and append the resulting `**Thread Metrics:**` block directly to the final response.

## Auto-Commit Protocol
- **Git Auto-Pull & Pre-Flight:** Before any agent begins work on an established git project, it MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` to perform all pre-flight routines (evaluating `ag-quota` velocity, auto-pulling/rebasing latest git changes, etc.) in a single step.
- **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to delegate the commit process. Auto-commit automatically requires a descriptive commit message detailing the changes made (generated via LiteLLM from staged diff/files) and pushes the commits (`git push`) to the remote repository.
- **Post-Flight:** Before concluding any turn or committing, agents MUST run `python3 /Users/matt/projects/ai-os/scripts/postflight.py` to retrieve and append live thread metrics and token counts to their responses.

- **Interactive Handoff & Spawn**: Never run agents blind (do not use `--non-interactive`, `--print`, or background execution without attachment). Handoffs must be run interactively to allow the user to review the plan and steering instructions. The handoff command MUST execute the `handover.py` script, which replaces the current process (`os.execvp("agy", ...)`) to attach the interactive `agy` CLI session directly to your terminal. Execute the handoff by running:
  `python3 /Users/matt/projects/ai-os/scripts/handover.py --to-model pro --completed "<what you analyzed/researched>" --next-steps "<what needs to be done next>"`
- **Exclusively Use agy for Subagents**: When agy quota is high/abundant, use agy exclusively. If a prompt goes to Hermes (default), use the MCP tool to spawn a tmux-bound `agy` CLI instance as a subagent, or if already in agy, have agy spin up its own subagent natively. Do not spawn external API agents or run subagents without attaching/steering capabilities.
