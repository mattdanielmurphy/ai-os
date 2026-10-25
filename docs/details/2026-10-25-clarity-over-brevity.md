# Clarity over brevity rule

## 22:05 Brevity rule now puts clarity first

Matt said replies had become too concise to understand, citing "You: rename 3 states, add Paused in Workflow settings...". The coordinator asked for the rule to favour clarity.

### What changed
- `.rules/core_safety.md` "Every Word Costs Matt": new "Clarity beats brevity" bullet (full sentences; say where, why, what it means; no "You:" prefixes or jargon; bold point-form stays). Budget is now "aim ≤ 50, up to 100 for clarity"; lines are full sentences (~12-20 words) instead of a hard 12-word max. Self-check now starts with a "would this make sense cold?" reread. The example's "After" used the exact "You: turn on auto-login" shorthand, so it was rewritten and the old version kept as the bad example.
- Rebuilt CLAUDE.md, LEAF.md, GEMINI.md via build_rules.py.
- `~/.claude/CLAUDE.md` (not in git) and `docs/coordinator/project-instructions-slim.md` updated to match.

### Rejected
- Dropping the word budget entirely: Matt still wants short replies; the problem was shorthand, not length.

### Not done
- The live claude.ai project instructions are only updated when the coordinator pastes the slim file in.

### Undo
`git revert` this commit; revert the two lines in ~/.claude/CLAUDE.md by hand.
