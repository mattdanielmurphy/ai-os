<!-- context-alert parent-thread: cmsg_01CUPXyY9oUwKVDFREVDpYDr9P7WaoyS3HMfJr3ooPw2Wu -->
# Handoff: CMPUT 174 Lab 4 skeletons (3 .py + 3 .md) (2026-10-23, cold)

## Chain
- Old thread: 54121438-83c6-4dfe-b794-3692c6092be3 (`<relay from="coordinator" session="session_0175dXAkvCYB1vDDWitTwHcr" current-tim`). Reopen with `claude --resume 54121438-83c6-4dfe-b794-3692c6092be3` (expensive: cold cache).
- Earlier handoff files under docs/handoffs/: none mentioned in the conversation.

## Chain summary
- Matt has public published Google Docs describing CMPUT 174 software labs; an earlier AI (Gemini/Antigravity/ChatGPT) once turned a lab page into files for him.
- Lab 4 is due **Fri Oct 23 at 20:00**. The doc describes 3 parts, each needing its own Python file.
- The coordinator session relayed the task; Matt then repeated the full request in the project thread (cmsg_01CUPXyY9oUwKVDFREVDpYDr9P7WaoyS3HMfJr3ooPw2Wu).
- Lab URL (public): https://docs.google.com/document/d/e/2PACX-1vRJUwe5DvSa41x182x4oimR-6DaVbDTzrQzXMex_ORDe7affmWKI64hnM6l7e2BgQ/pub
- The old thread's only logged output is "I sent Matt the reply in the thread with the details file attached." Nothing in the transcript shows any file being created, so assume **no lab files exist yet**. Check before writing.

## This thread
- Done: nothing verifiable. No fetch of the lab page, no files, no commits are visible in the transcript.
- Tried and failed: nothing recorded.
- The final turn was a wake on Matt's repeated message; it ended with "No response requested", so the work did not start.

## Working on now
Build the Lab 4 deliverables from the published doc: for each of the 3 parts, one Python skeleton and one markdown file with the instructions and sample output. It stopped before any work: the doc hasn't been fetched and the labs folder hasn't been located.

## Keep in mind
- **Labs folder**: find the "designated labs folder" via `~/projects/ai-os/docs/SCHOOL.md` (read `~/projects/ai-os/docs/ABOUT_MATT.md` first). If SCHOOL.md is over a week old, refresh it per its steps. Otherwise search the Mac (QMD, `mdfind`). Check whether earlier labs have a naming convention and copy it.
- **Fetch the page directly** (it's public): `curl -sL <url>`. Don't drive Matt's Chrome tab unless that fails. If you do, show the claude-control banner first (`~/.hammerspoon/bin/claude-control ask "<why>" 3 --thread <id>`, then `done <ticket>`).
- **Write no meaningful code.** Only `def` lines with the exact function names, parameter names and spelling from the doc. No bodies beyond `pass` (or a docstring/comment). This is a school assignment.
- **Python files**: put every required step in comments, so Matt deletes each comment as he implements it. Mark **every comment you write yourself** with `# !important` (his VS Code extension highlights it). Assignment-derived step comments are the ones that are not marked, so keep the two clearly distinguishable.
- **Markdown files**: the instructions and sample output, copied **exactly** as published, 100% accurate. After writing, **diff each sample output against the fetched source text** to verify. Preserve whitespace, punctuation and typos exactly.
- **Contradictions**: study the programs and compare sample outputs. Flag any internal contradiction, typo or discrepancy in the lab (for example, two sample outputs that can't both match). Matt will ask a TA, so he needs to know before he picks one to match. Mark these `# !important` in the code and list them in your reply. Don't over-analyze; basic inconsistencies are enough.
- **Reply style** (Matt's rules): ≤50 words (cap 100), the answer on line 1, one idea per line, bold the point, blank line between lines, max 4 items. Put important items (contradictions, anything untested) in the reply, not only in files. Link every file and folder you mention with `python3 ~/projects/ai-os/scripts/file_link.py <path>`.
- **Details file**: append `## HH:MM <topic>` to `~/projects/ai-os/docs/details/2026-10-23-<thread-slug>.md`. Link it on the last reply line, attach it in the project thread (SendUserFile), and commit and push it (always push).
- **Other rules**: use `bun`, not npm. Temp files go in `./tmp/` or the scratchpad, never `/tmp`. Don't `rm` outside scratch dirs. Run the skeletons (`python3 -I` or an import check) to confirm they parse, and report the result honestly.
- **Reminder**: the deadline is tonight at 20:00. Consider adding an Apple Reminder (`apple-reminders add`) if none exists.
- Matt says TAs are lenient: 1 mark for showing work in progress, 3 for the code demo. He still wants to be told about any discrepancy.

## Next steps
1. Run `curl -sL "https://docs.google.com/document/d/e/2PACX-1vRJUwe5DvSa41x182x4oimR-6DaVbDTzrQzXMex_ORDe7affmWKI64hnM6l7e2BgQ/pub" -o <scratchpad>/lab4.html` into a fresh scratchpad directory. Extract the text, then read ABOUT_MATT.md and SCHOOL.md to find the labs folder. Create the 3 `.py` + 3 `.md` files with the exact names the doc gives. Diff the sample outputs against the source text. Then write the details file and reply to Matt.

## Read first
- `~/projects/ai-os/docs/ABOUT_MATT.md`: where courses and labs live.
- `~/projects/ai-os/docs/SCHOOL.md`: the CMPUT 174 labs folder, schedule and due dates.
- `~/.claude/CLAUDE.md`: reply-length, linking, details-file and `# !important` conventions.
- Earlier labs in the labs folder (Lab 1 to 3, if present): the naming and layout convention to match.

Paste into a new thread: "Read /Users/matt/projects/ai-os/docs/handoffs/2026-10-23_relay-from-coordinator-session-cold.md and continue. Then: I like that you left my first fn in cipher1 but I want you to give the rest of it the same treatment.
And please make the instructions super clear, I have to bang this out"
