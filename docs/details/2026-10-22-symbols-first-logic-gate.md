# Symbols-first logic gate (2026-10-22)

## 14:40 Symbols-first ladder for the habit gate

Asked (via coordinator): the gate's FOL Five page jumped to symbolization before Matt knows the symbols. Rebuild the question ladder so it starts with symbol flashcards and only moves on when solid; replace today's page now.

---

### Today's page replaced

Same link (https://claude.ai/artifact/KbgoxmBsydpVAAgcQaery4), now 5 cards: what ∀, ∃, ¬, ∧, ∨ mean. The old page had no saved taps, so nothing was lost. The remaining symbols (→, ↔, =) come first next time, since the ladder serves never-right cards before seen ones.

---

### How the ladder climbs

`services/checkin/logic_rungs.json`, six rungs: symbol → meaning, word → symbol, predicates/names/variables, reading one-quantifier formulas, symbolizing one-quantifier sentences, then agent-written Unit 5 mixed questions. The first five are fixed card banks (written once, checked, so no agent invents questions). Moves up only when every card in the rung has been answered right at least once AND the last page scored ≥ 80%. A page under 50% steps back one rung (habits rule: pull back after misses). Skips change nothing on the ladder (the study ladder already shrinks the dose). Misses come back first on the next page. State: `data/logic_rung.json`.

Rejected: advancing on a single perfect page (too fast; he could pass a rung having seen only 5 of 8 symbols), and time-based advancing (ignores whether it stuck).

---

### Scoring hook

When he replies 👍/done to the gate, the agent reads the page's taps (ArtifactData, practice/<date>) and pipes them to `habit_gate.py score <date>`. Untested end to end: depends on the agent following the hint. Today was already marked skipped earlier, so today's taps get scored only if he 👍s in this thread.

### Undo

`git revert` the "Habit gate: symbols-first question ladder" commit; delete `data/logic_rung.json`.
