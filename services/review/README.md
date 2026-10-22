# Review page

One scrolling artifact page for reviewing a long agent reply: a card per section, a "Read, and I'm good
with it" tick, and one comment box per section. Tap a sentence to aim the box at it (tap again or "general"
to go back); drag over words to narrow it. A sentence with a note brings it back when tapped again.

- Build: `python3 build.py REPLY.md --id <id> --title <t> --thread <cmsg_…> --out <scratchpad>/x.html`,
  publish with `capabilities: {db: {}}`, then rebuild with `--page <artifact id>` and publish again.
- Results: db `reviews/<id>` → `{sections: {s1: {read, general, notes: {key: {quote, text}}}}, finishedAt}`.
- Done button links to the Mac connector's `/act/<act token>/review-done` route; the Mac queues a note for
  the coordinator, which routes it to the thread. Base URL comes from `tmp/mac-connector-act-url`.
- Look comes from `../pages/kit.css` (shared with the check-in page; check-in still has its own copy, to migrate).
