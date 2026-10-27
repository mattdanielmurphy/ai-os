# Linear board questions (2026-10-27)

## 07:20 Projects vs issues, free tier, self-hosted alternatives

Matt asked three things: should many board issues be Linear Projects, what the free tier includes and how soon he'd pay, and whether there's a free self-hostable alternative. I read every issue on team MAT through the Linear connector (it worked from the Mac), checked Linear's pricing page and docs, and searched for alternatives. Nothing was changed on the board.

---

### Which issues should be projects

Rule of thumb: a Linear **Project** is a body of work with several steps and (usually) an end; an **Issue** is one step. Several board cards are really projects with no steps inside them, which is why the board feels off.

Recommended to become projects (each gets its real next steps as issues):

- **Slub Utils** (MAT-10), **Explainer reels** (MAT-14), **qwerty MIDI plugin** (MAT-12), **UI Mixer** (MAT-15), **Live call transcript with Tyler** (MAT-31), **Morning check-in and habit ladder** (MAT-23), **ai-os agent setup** (MAT-30), **Daily mini crossword** (MAT-13).
- **Each course** as a project: PHIL 120 (MAT-5), CMPUT 174 (MAT-6), World Music (MAT-7). Then the World Music autoethnography (due Oct 30), Lab 5, the midterms etc. become dated issues inside them, so due dates show up properly.
- **Life OS** (MAT-34) and **Mac inventory** (MAT-29) could be projects later, once they have steps.

Better as an **Initiative** (Linear's grouping above projects): **Slub company with Tyler** (MAT-9), holding the Slub projects. Initiatives may be limited on the free plan; check before relying on them.

Stay as issues: every parked idea (MAT-35..41), and one-offs like monthly budget, part-time job, pickleball, the dictation re-test, the palette pick (MAT-16), HUD slots review (MAT-32).

There's already one project, "atlas calculator", sitting in Backlog with nothing in it.

---

### Trade-off of moving to projects

Projects don't use the team's columns (Idea / Planned / Live on Mac / Paused / Done). They have their own project statuses (Backlog, Planned, In progress, Paused, Completed, Canceled), and custom project statuses need the Business plan. So the main board would show steps, and a separate Projects view would show the projects. Converting is reversible; nothing is lost.

---

### Free tier limits

From [linear.app/pricing](https://linear.app/pricing) and the [billing docs](https://linear.app/docs/billing-and-plans):

- 250 issues, 2 teams, unlimited members, 10 MB per upload. All members are admins.
- Next plan is Basic at $10 per user per month (yearly), so $10/month for Matt alone. Basic raises teams to 5.
- If over 250 on Free: nothing is deleted, you just can't create new issues.
- Matt has 39 issues total (4 are Linear's canceled welcome cards). At ~10 new cards a week that's roughly 5 months to 250 if nothing is ever archived.
- Archiving: I could not confirm from Linear's current page whether archived issues count toward the 250. If they don't (secondary sources suggest archiving keeps you free), turning on auto-archive for Done/Canceled keeps him free indefinitely. Worth a 2-minute test when near the cap.
- Projects themselves aren't issues, so moving things into projects doesn't cost issue slots by itself; the steps inside them do.

---

### Self-hosted alternatives

- **[Plane](https://plane.so)** Community Edition: the closest to Linear (issues, cycles, modules, pages), AGPL, Docker. Heavy: needs Postgres, Redis, a queue and object storage; docs suggest about 2 CPUs and 4 GB RAM. That's "big" for his VPS, so it needs his OK first.
- **[Vikunja](https://vikunja.io)**: one small Go binary plus a database, kanban boards, light enough to be little risk on the VPS. Much less polished than Linear.
- **[Huly](https://huly.io)**: all-in-one (Linear + Notion + Slack), very heavy to self-host.

Sources: [openalternative.co](https://openalternative.co/alternatives/linear), [toolradar](https://toolradar.com/guides/best-open-source-project-management-tools).

---

### My recommendation

Stay on Linear free. He's at about 15% of the cap, and agents already park ideas there through the Linear connector; switching would mean rebuilding that. Revisit only if he nears 250 and archiving doesn't free slots. If he still wants self-hosting, Vikunja is the safe one for the VPS; Plane needs a 👍 because of its size.

Untested: whether archived issues count toward 250; whether Initiatives are on the free plan.

Undo: nothing changed.

## 07:35 Separate Slub workspace, moving projects, more generous alternatives

Matt noticed the board is turning into a Slub board, floated a second Linear account under his slub.cc email (keeping this one personal), asked whether a project can be moved between Linear accounts easily, and whether there's something nearly identical to Linear with a more generous free tier.

---

### Two workspaces, not two accounts

Linear's unit is the **workspace**, and one login can belong to several workspaces and switch between them from the workspace menu. So he doesn't strictly need a second account: he can create a "Slub" workspace (signed up with or owned by his slub.cc address if he wants company stuff under the company email) and keep "mattmurphy" personal.

Why this is a good split:
- The free plan is per workspace, so two workspaces = 250 issues each.
- On the free plan everyone is an admin and private teams need Business, so if Tyler joined the current workspace he'd see all the personal cards (job, budget, therapy-harness idea). A separate Slub workspace avoids that, and members are unlimited on free.
- Agents' Linear connector is signed in to one workspace at a time; using a second one means connecting it too (Linear's connector can be re-authorized per workspace). Untested which workspace the current connector would pick.

---

### Moving projects between workspaces

- Linear's docs (Exporting data, FAQ) say teams can be moved between workspaces by importing them from one Linear workspace into another. That's the whole team with its issues, not a single project.
- There's no one-click "move this project to another workspace". Options: put Slub work in its own team first and import that team; or CSV export and re-import; or I copy cards across with the API/connector.
- Within one workspace, moving issues between teams is one click (or bulk select).

Suggested path: make a second team "Slub" in the current workspace now (free allows 2 teams), move the ~16 Slub-labelled cards into it, then when the Slub workspace exists, import that team over. Nothing is lost if he changes his mind.

---

### Alternatives with a more generous free tier

- **[Plane Cloud](https://plane.so/pricing)** (hosted, no VPS): free for up to 12 users; the pricing page lists no work-item cap. Has a Linear importer, cycles, modules, pages. Free plan lacks exports, integrations (GitHub/Slack), templates and dashboards; no exports on free is a lock-in risk. Closest look and feel to Linear.
- **GitHub Projects**: free and effectively unlimited, and agents already use GitHub fluently. Far less polished as a board.
- **Jira free**: 10 users, but nothing like Linear's feel.

Not recommended: Height (shut down), Huly cloud (reported winding down, unconfirmed).

---

### Recommendation for this round

Stay on Linear and split into two free workspaces (personal + Slub). That doubles the free room, keeps Tyler out of personal cards, and keeps the agent connector. Plane Cloud is the fallback if the cap ever bites.

Untested: Linear-to-Linear team import (documented, not tried); whether the connector can hold two workspaces at once.
