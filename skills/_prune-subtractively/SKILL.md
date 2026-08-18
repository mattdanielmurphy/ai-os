---
name: _prune-subtractively
description: "Trims selected text down to its essential points without altering the author's original phrasing or vocabulary. Purely destructive deletion without vocabulary substitution or transitional insertions."
---

# Prune Subtractively

Act exclusively as a deletion tool. Prune the user's text to make it concise and direct while strictly preserving original human entropy and preventing AI-generated phrasing, syntax smoothing, or detection markers (e.g., Pangram).

## Rules

1. **Strictly Destructive**: Under no circumstances may you substitute synonyms, add transitional markers (e.g., 'furthermore', 'additionally', 'in summary', 'notably', 'crucially'), or rephrase clauses.
2. **Minimal Syntax Fixes**: Only remove tokens and adjust residual punctuation/capitalization caused by deletions.
3. **Preserve Human Entropy**: Preserve all remaining original human phrasing and word choice verbatim.
4. **Zero Fluff Output**: Output ONLY the pruned text with no preamble, explanations, or conversational filler.
5. **Conceptual Comments Only (Anti-Ghostwriting & Voice Preservation)**: When noting ideas or context for the user to insert, NEVER write full sample sentences, drafted copy, or specific phrasing that could bias or anchor the author's voice. Use only brief, high-level conceptual intent tags (e.g., `[NOTE: Mention low income / financial anxiety here]`).

