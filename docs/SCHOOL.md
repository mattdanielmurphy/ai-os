# School snapshot (UAlberta, Fall 2026)

**Last refreshed: 2026-10-20 (Tue evening), from syllabi + Canvas.** If this date is more than a week old, refresh it (steps at the bottom) before relying on "where he is".
All times Mountain. Course files: `~/Documents/School/<course>/`.

## Weekly schedule
| Day | Time | What | Where |
|---|---|---|---|
| Mon/Wed/Fri | 10:00–10:50 | MUSIC 102 World Music (LEC A01, Dr. Rachel Colwell) | SAB 331 |
| Mon | 19:00 | XImE ensemble (MUSIC 193A LCL X01) | FAB Studio 2-7 |
| Tue/Thu | 8:00–9:20 | CMPUT 174 lecture (LEC A1, Sadaf) | CCIS L1160 |
| Wed | 18:00–21:00 | PHIL 120 Symbolic Logic (LEC X01, Hassan Masoud) | ESB 2-35 |
| Thu | 11:00–13:50 | CMPUT 174 lab (LAB D17; TAs Ujjwal Bhatia, Sai Vashnavi Jattu) | UCOMM 2-140 |

Office hours: Colwell Wed 11–12 (Arts 3-34A); Masoud Fri 10–11 (Assiniboia 2-67).
No classes Reading Week Nov 9–13. XImE: Oct 26 is an open improv session at Absurd (8107 102 St NW), 19:00.

## Upcoming dates
| Date | Course | Item |
|---|---|---|
| Wed Oct 21, 10:00 | World Music | **Midterm**, in class, 50 min (20%). Bring pens. |
| Thu Oct 22, 20:00 | CMPUT 174 | **Quiz 2** closes (opened Oct 20 8:00; 30 min timed, 4%) |
| Fri Oct 23, 20:00 | CMPUT 174 | **Lab 4** due (User Defined Functions II) |
| Thu Oct 29, 20:00 | CMPUT 174 | Respondus LockDown Browser test due |
| Fri Oct 30, 20:00 | CMPUT 174 | Lab 5 due |
| Fri Oct 30, 23:59 | World Music | **Autoethnography** (2 songs, 2 pages double-spaced, works-cited page, no footnotes; 20%) |
| Wed Nov 4, 18:00 | Logic | **Midterm 2** (30%; likely Units 4–6) |
| Thu Nov 5, 8:00–16:00 | CMPUT 174 | **Midterm** (60 min, Respondus, 22%) |
| Fri Nov 6 | World Music | Units 4–5 quiz, in class |
| Thu Nov 19 / Fri Nov 20 | CMPUT 174 | Quiz 3 / Lab 6 |
| Fri Nov 27 | CMPUT 174 | Lab 7 |
| Wed Dec 2, 18:00 | Logic | **Final** (2 h, 50%) |
| Wed Dec 2 | World Music | Unit 6 quiz, in class |
| Thu Dec 3 / Fri Dec 4 | CMPUT 174 | Quiz 4 / Lab 8 |
| Fri Dec 4, 23:59 | World Music | Live performance video essay (submit any time before; 10%) |
| Dec 9–22 | CMPUT 174, World Music | Finals (dates TBD on the Exam Schedules page) |

## Where he is
- **CMPUT 174**: Week 8 of 15, Module 7 (multidimensional lists). Done: orientation quiz, Quiz 1, Labs 0–2 (graded). Lab 3 submitted, not yet graded. Next: Quiz 2 and Lab 4 (no `labs/lab_4` folder yet). Midterm review week of Nov 2.
- **World Music**: finishing Unit 3 (identity, community & activism; last class Mon Oct 19, Freedom Songs). Unit 1 and 2 quizzes done. Next: midterm Oct 21, then Unit 4 (music & sensory experience; Deaf music Oct 23). Autoethnography: only a brainstorm in `World Music/Unit 3/My Identity.md`, songs not chosen yet. Live performance essay not started.
- **Logic**: Unit 5 (FOL language & syntax, forall x Part V, ch. 23–29), week 7 of 11. Midterm 1 done (graded). Unit 4 (TFL natural deduction) finished; recommended practice: ch. 17 set C, ch. 18 sets A/C/D, ch. 22 set B, plus the Canvas "further exercises" pages for Units 4 and 5. Next: Unit 6 (FOL semantics) from Oct 28, Midterm 2 Nov 4.

## How to refresh this file
1. Static facts (times, rooms, weights) come from the syllabi: `CMPUT 174/174_Fall_2026_Course_Syllabus.md`, and `pdftotext -layout` on the World Music and PHIL 120 syllabus PDFs.
2. Canvas: open `https://canvas.ualberta.ca/api/v1/users/self` in the built-in browser pane (Matt is signed in there), then run the contents of `scripts/canvas_school_snapshot.js` with the browser javascript tool. It returns sections, every assignment with due date and submission state, module names, the last two weeks of announcements and the next three weeks of calendar events. Read-only.
3. CMPUT lab times/rooms: the "Lab Schedule" Google Sheet linked in the CMPUT Canvas "Lab Information" module (needs the UAlberta Google sign-in in the pane; fetch `.../pubhtml/sheet?headers=false&gid=0` from the page and grep for `D17`).
4. Update "Where he is", drop past rows from the upcoming table, bump the refreshed date. Commit and push.
