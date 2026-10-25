# smartc2p → OpenRouter (2026-10-25)

## 01:16 OpenRouter hookup + review

Ask (via coordinator): find smartc2p, hook it to OpenRouter with a cheap Pareto-frontier model, review and modestly improve, commit, push.

Found `~/projects/smart-c2p` (globally linked via bun as `smart-c2p`). A code2prompt wrapper: a model picks include/exclude flags, then it copies the codebase to the clipboard, or `--ask` answers questions. It used Gemini SDK first with an OpenRouter fallback. It had no git remote.

---

### model pick why

Live OpenRouter `/api/v1/models` pricing, 2026-10-25. The workload is almost all input (a whole codebase per ask, short answers). Candidates ($/M in / out):
- deepseek/deepseek-v4.1-flash: 0.02 / 1.00, 1M ctx, flat at any size. **Picked.**
- openai/gpt-6-luna: 0.10 / 0.50, doubles over 272k.
- anthropic/claude-haiku-5.5: 0.10 / 0.50, jumps to 0.50 / 2.50 over 100k.
- qwen/qwen3.7-flash: 0.03 / 0.13 under 32k, then 0.10–0.20.
- google/gemini-2.5-flash (old default): 0.30 / 2.50.
DeepSeek is 5x cheaper on input than the next good option with no size tiers. Quality not benchmarked by me; if answers feel weak, `--model openai/gpt-6-luna` is the step up.

---

### code changes made

- One OpenRouter path (`chat()`); Gemini SDK removed.
- Key: env `OPENROUTER_API_KEY` or `~/.config/smart-c2p/.env` (created with an empty line, chmod 600).
- Bug fixed: `--thread` follow-ups never resent the codebase, so the model lost the code after turn 1.
- Cost now from OpenRouter's `usage.cost`, not hard-coded Gemini rates (which were wrong anyway).
- Flags cleaned of code fences / leading `code2prompt .`.
- `--model` flag + `SMART_C2P_MODEL`; bun.lock added to excluded lockfiles; lstat (no symlink loops).
- Untracked committed node_modules, added .gitignore + README, private repo github.com/mattdanielmurphy/smart-c2p.

---

### untested with real key

Tested with a stubbed fetch: help, missing-key error, `--out`, `--ask`, thread follow-up (4 messages incl. system). Not tested against the real API: no OpenRouter key exists on the Mac (the `.zshrc` line is commented out).

Side note: `~/.zshrc` holds several API keys in plain text (some in comments). Worth moving to an .env.

Undo: `git -C ~/projects/smart-c2p revert HEAD`.

## 01:22 Switched default to GPT-6 Luna

Matt's call from Artificial Analysis: Luna's cost per task is $0.07 vs $0.26 for DeepSeek V4.1 Flash (1017); DeepSeek scores higher (45 vs 38 intelligence) but the extra isn't needed for picking flags and code Q&A. Default is now `openai/gpt-6-luna`. Stub-tested; still no real key.

---

### luna large prompt price

Luna doubles to $0.20/M input past 272k prompt tokens, so very large codebases cost 2x per ask. Fine for most of his projects.

Note: his screenshot compared the "1017" DeepSeek variant ($0.15/$0.60 on OpenRouter); my earlier pick was the plain `deepseek-v4.1-flash` ($0.02/$1.00). Doesn't change the choice.

## 01:25 Reasoning effort low, not Max

Matt noted his AA comparison was at Max effort only to compare like to like; he doesn't want Max. Requests now send `reasoning: { effort: "low" }` (OpenRouter's unified param). Override with `SMART_C2P_EFFORT` (none/minimal/low/medium/high). Rejected `none`: low keeps a little thinking for flag picking at tiny cost. Stub-tested (request body carries effort low).

Fix: the repo's https push needed a credential helper; set `credential.helper` to `gh auth git-credential` in smart-c2p's local git config.

## 01:28 Is Luna really right

Matt asked if I truly agree. Yes, but on different grounds than AA cost per task.

---

### cost per task misleads here

AA's cost per task is measured on its benchmark suite at Max effort, which is dominated by reasoning/output tokens. smart-c2p is the opposite: a huge input (whole codebase) and a short answer at low effort. So per-ask cost is basically input price × codebase size. At 100k tokens in / 1k out: Luna ≈ $0.0105; DeepSeek V4.1 Flash on a solid fp8 host (DeepInfra $0.112/$0.336) ≈ $0.0115. A near tie, and both are about a cent.

---

### my first pick was flawed

The $0.02/M DeepSeek price I quoted was OpenRouter's cheapest endpoint (OpenInference, fp4 quantization). Default routing would favour such hosts; quality on fp4 hosts can be below what AA benchmarked. Real DeepSeek hosts run $0.10–$0.30/M. I should have checked `/endpoints`, not just the headline price.

---

### why luna wins anyway

- AA-LCR (long-context reasoning, the benchmark that matches "read this codebase and answer") is a tie: 83% vs 83%.
- DeepSeek's lead is on agentic/terminal benchmarks smart-c2p doesn't use.
- Luna is served first-party (OpenAI/Azure/Bedrock): consistent quality, no fp4 lottery, same price.
Kept: `openai/gpt-6-luna`, effort low. Lesson: compare per-endpoint prices and workload shape (input vs output) for frontier picks.
