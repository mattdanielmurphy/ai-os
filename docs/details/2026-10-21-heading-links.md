# Heading links in replies (2026-10-21)

## 18:35 Test status and proposed rule

Asked (via coordinator, Matt's idea from the Tyler utils thread): test whether `file.md#heading` links in replies open the details file at that heading; if yes, make each non-trivial reply line link to its own heading.

What I did: started writing my own test file, then the coordinator said the Tyler utils thread had already posted a 4-link demo and asked Matt to tap them. I dropped my duplicate test so Matt isn't asked twice. His answer there decides it.

Known so far: the platform docs say a `/mnt/project-files/<file>.md#<slug>` link opens the preview at that heading. Mac paths (`/Users/matt/...#slug`) in Code-tab replies are untested.

Proposed rule (waiting on Matt's 👍 and his tap result): each non-trivial reply line links to its matching `##` heading in the details file; the bold point stays readable on its own, so anything important is still said in chat, never only behind a link. The final "Details:" line stays.

Rejected: changing the global rule before Matt confirms the links actually land on the heading.

Undo: nothing changed yet.
