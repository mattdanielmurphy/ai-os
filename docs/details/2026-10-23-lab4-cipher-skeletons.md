
## 13:15 cipher1 same treatment as cipher2/3

Matt asked: keep his first functions in cipher1.py, give the rest the cipher2/3 treatment, make instructions super clear.

What I did: kept his `ask_for_claim_filename` and `read_packets` untouched. Replaced the loose comment dump with `def` skeletons (`scramble`, `select_packets`, `main`), each holding the lab's own steps (unmarked) plus plain-English `# !important` hints. No working code written (bodies are `pass`).

Checks: file parses. In a scratch run (not saved) I followed my hints literally on files 1, 2, 3 and got all three sample outputs exactly, so the hints are right.

Left for Matt: his test call `read_packets("1")` is global code (Quality Req 1.3); flagged to delete. Add a `main()` call as the last line. Note he renamed signal1-3.txt to 1/2/3; the sample output shows `signal1.txt`, so for the demo either name works but the TA will see the typed name.

Undo: `git revert` the "Lab 4 cipher1: skeletons" commit in cmput-174; the pre-edit copy is also in the session scratchpad.
