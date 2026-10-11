# Morning Flow Auto-Advance and Single Nudge

- Changed post-threshold morning review to dispatch each remaining due FSRS card automatically, then complete the flow when due cards are exhausted.
- Reminder state now tracks the latest nudge. A new reminder retires the prior message, and “I’m up” replaces the tapped nudge with the active stage. Stale nudge callbacks cannot acknowledge or disable the latest reminder.
- Updated morning-flow context and regression coverage for automatic continuation, nudge replacement, acknowledgment, and stale callbacks.
- Verification: focused morning-flow/nudge tests passed (2 passed). Full assistant suite had 23 passing tests and one unrelated existing failure in a feedback-copy assertion (`test_active_card_conversational_meta_comment_and_button_hierarchy`).
