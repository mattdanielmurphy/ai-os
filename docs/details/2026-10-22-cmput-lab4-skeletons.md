# CMPUT 174 Lab 4 skeletons (2026-10-22)

## 21:30 Lab 4 files

**Asked:** extract the Lab 4 (Cipher Relay) instructions into a .md per part, plus .py skeletons with function declarations only and the steps as comments; sample output 100% exact; flag doc contradictions with `# !important` comments. No real code.

**Where:** `~/Documents/School/CMPUT 174/labs/lab_4-central-command/` (folder already existed with Matt's `cipher1.py` and signal files named `1`, `2`, `3`). Committed and pushed to the private `cmput-174` repo (`ddadd97`), only my new files.

---

### Files made

- `cipher1.md`, `cipher2.md`, `cipher3.md`: doc text word for word; purple-highlighted text rendered **bold**; sample output in code blocks; my notes start with "!important (Claude)". `cipher3.md` also holds the demo questions, submission steps and marking.
- `cipher2.py`, `cipher3.py`: header docstring in his Lab 3 style, every required `def` with `pass`, the doc's steps as comments inside each function. Functions carried over from earlier parts say "paste your previous version" (doc tells you to duplicate the previous part).
- `signal1.txt`–`signal3.txt`: byte-identical copies of `1`–`3` so the demo matches the sample output's filenames.
- `cipher1.py`: **not rewritten** (his work in progress). Added one `# !important` line above `ask_for_claim_filename()` about the wrong prompt. Not committed (his WIP).

---

### How the sample output was verified

- Direct fetch of the published doc needs a UAlberta sign-in, so I opened it in a new Chrome tab (claude-control light banner granted), read it, then closed the tab.
- Computed SHA-256 of all 12 table cells (sample outputs, strength table, demo code) in the page and of my local copy: identical (`14d9229e…51f6e5d4`).
- A script extracted every code block from the three .md files and compared it to that verified copy: 11/11 match.
- A private checker (scratchpad only, never in his folder) ran the spec on his signal files: all 9 sample outputs reproduced exactly. So no internal contradiction between steps and sample output.

---

### Discrepancies found

- Part 2/3: labels `Chain 1 before: ` etc. appear only in the sample output; steps just say "Print chain_1".
- Part 3: empty line after every round (including the last) appears only in the sample output.
- Part 1: "Print the keystream" is numbered as top-level step 5 instead of a `main()` sub-step (formatting slip).
- Part 3: no sample goes over strength 14, so "Both are unstable." and the one-over-14 rule are untested by the samples. Exactly 14 (signal1 round 1) counts as stable.
- His `cipher1.py`: prompt `Enter claim filename: ` should be `Enter a filename: `; top-level `read_packets("1")` breaks SQR 1.3.
- Demo Q3: text lists (Q, X, K, Z) but code order is Q, X, Z, K. Typos: ‘QXZ' quotes, "fixed list..".
- "has the word ERROR": files only contain exact `ERROR` lines, so either check works.

---

### Undo

`git revert ddadd97` in the course repo; delete the `# !important` line in `cipher1.py`.
