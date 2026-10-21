---
name: _review-voice-calls
description: Review Matt's claude.ai voice-call transcripts (Obsidian "Voice calls/") and act on them. Use for the "Review unsaved voice calls" / "File voice call" tasks from the voice bridge, or when Matt asks to go over his voice chats.
---

# Review voice calls

1. Print the transcripts (frontmatter and tool markers stripped):
   `python3 ~/projects/ai-os/scripts/review_voice_calls.py "<vault-relative path>" ...`
   (no args = every transcript not yet marked reviewed). Read `docs/ABOUT_MATT.md` too, so you only file what's new.
2. **Facts** about Matt or his setup (gear, home, car, habits, preferences, how voice Claude behaves):
   - durable facts about him → `docs/ABOUT_MATT.md` "Right now" (pointers, short lines; nothing sensitive)
   - voice-Claude behaviour and bridge quirks → `docs/VOICE_TASKS.md`
   - lasting working preferences → Claude memory + `.rules/` (then `scripts/build_rules.py`)
   Skip what voice Claude says about itself unless Matt tested it; skip chit-chat.
3. **Reminders**: anything he says he needs/wants to do → `apple-reminders add` right away (sensible due time, notes = which call). Default to creating.
4. **Calendar events / emails**: only if he asked; list what you'd do and ask (emails need his yes).
5. **Ideas / builds he floated** (e.g. a gas-price tracker): don't start them. List them in the reply and ask which, if any, to pursue; flag big builds.
6. Mark done: `python3 ~/projects/ai-os/scripts/review_voice_calls.py --done "<path>" ...`
7. Commit only your files (`scripts/auto_commit.py -m "..." --paths ...`), then reply: filed / reminders made / ideas waiting on him.
