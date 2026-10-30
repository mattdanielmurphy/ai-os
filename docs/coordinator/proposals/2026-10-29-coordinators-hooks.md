# Coordinators + hooks, and how rules get changed (proposal, 2026-10-29)

Status: **proposal only. Nothing built, no rule changed.** Each section ends with the decision Matt needs to make.

## 1. Rule changes: proposed, agreed, then saved

**Problem.** Matt: rules are changing "way too quickly… I don't even know what the rule is exactly." Today's hook (`rule_prompt_nudge.py`) tells every agent to save rule-language "this turn", and `rule_promise_guard.py` blocks a turn that promises without saving. So the system currently *rewards* the fast, unilateral edits he dislikes. Example: the subject-coordinator threshold changed three times in four minutes.

**Proposed flow.**
1. **Draft.** When Matt states a standing preference, the agent writes it to `.rules/pending/<date>-<slug>.md` in the same turn. Pending files are *not* compiled into CLAUDE.md/GEMINI.md and do not reach Tyler.
2. **Show.** The reply shows the exact wording, what it replaces (quoting the old line), and one line of why. Ends with `**Actions:** 1, Save this rule as written | 2, Let's change the wording | 3, Drop this rule`.
3. **Agree.** Only Matt's explicit yes (a button or plain words) moves it into `.rules/`, runs `build_rules.py`, commits, pushes. Wording changes loop back to step 2.
4. **Never lost.** A pending draft is on disk, so "promises to remember are saved" still holds: the draft *is* the saved promise. Unanswered drafts show up in the coordinator's daily status and the rules dashboard (PLAN §3.11) until he answers.

**Hook changes (small).** `rule_prompt_nudge.py` says "draft it to `.rules/pending/` and show Matt the exact text; save only after he agrees." `rule_promise_guard.py` accepts a new pending draft as proof of saving.

**Who may draft.** Any agent. The main coordinator should not *finalise* rules about itself without the draft step either.

**Open question vs PLAN §3.10.** That plan lets agents write live "beta" rules without asking (additive, max 5, expire in 21 days). That contradicts today's ask. Recommendation: keep beta, but only for the learn loop's small reminders, and every beta rule still gets shown to Matt in one line when it goes live. Matt decides.

**Decision:** approve this flow (and the exact hook wording, shown before it's changed)?

## 2. Proactive subject coordinators

**Current saved text** says: start a subject coordinator "as soon as more than one thread works on a shared subject".

**Honest pushback.** Two threads is too low. Each coordinator is another session to keep warm, another context to pay for, and another place a message can land in the wrong spot. Two threads on one subject is what the main coordinator already handles fine. Recommendation: start one at **3+ threads on a subject, or any subject expected to run more than a day**; archive it when done; project coordinators stay until Matt's clean-ups (unchanged).

**Decision:** 2+ (as saved) or 3+ / multi-day?

## 3. "Hooks pass messages to the right coordinator automatically"

**What hooks can really do.** A hook runs inside the session Matt typed into. It can add context, warn, or block, but it **cannot move his typed message into another session** before the model sees it. So true zero-hop routing isn't available.

**What is possible, cheaply:**
- In the main coordinator, a `UserPromptSubmit` hook matches the message against a subject registry (`coordinator/threads.json` + subject keywords) and adds "this is about Glass TV → forward to [Glass TV Coordinator] verbatim". The coordinator forwards with SendMessage in one tool call, no thinking. That's still a hop, but a cheap mechanical one.
- Best path is still Matt talking to the sub-coordinator directly. A pinned sidebar group per subject makes that easy.

**Decision:** OK with "hook flags, coordinator forwards" as the realistic version?

## 4. Per-project status reports from scripts

Good idea, low risk. A script reads each project's git log, open threads (list_sessions) and Linear issues, and writes a short status the coordinator can paste. No model needed for the gathering. Recommend building this first: it helps every other piece.

**Decision:** build this first?

## 5. Top-level inbox with domain coordinators (projects, school, health)

**Honest take:** right direction later, too early now. The project freeze (until the Tyler merge) says simplify, and three new standing coordinators is more structure. School is also sensitive: a school coordinator must never drift into writing coursework. Recommend: keep one inbox (the main coordinator), add domains only when a domain has 3+ live threads, starting with projects.

**Decision:** park as an idea in IDEAS.md for now?
