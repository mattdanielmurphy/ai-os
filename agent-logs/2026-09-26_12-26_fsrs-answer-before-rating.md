# Agent Work Log: FSRS Answer Before Rating

- **Date:** 2026-09-26 12:26 MDT
- **Goal:** Let Matt verify recall before choosing an FSRS difficulty rating.

## Root Cause

- Cards with stored options already used a multiple-choice answer and feedback stage. Cards without options fell back to the same Again/Hard/Good/Easy buttons without revealing an answer.
- FSRS review updates also rewrote option fields with defaults, which would have discarded generated choices after the first review.

## Changes Made

- Cards without options now request three distractors in one configured Codex call for up to five due question-answer pairs. Valid choices are stored with the correct answer at a randomized index and reused by manual and scheduled reviews.
- Existing multiple-choice feedback reveals correctness before rating. Optionless fallback reviews require an answer reveal before a rating is accepted.
- FSRS updates now preserve options and correct index; temporary answer-stage markers are removed when a review completes.
- Updated `AG_CONTEXT.md` and `DEVELOPMENT_JOURNAL.md`.

## Verification

- `la restart aios-assistant` unloaded and loaded `com.matt.agent.aios-assistant` successfully.
- Tests were not run in this turn.
