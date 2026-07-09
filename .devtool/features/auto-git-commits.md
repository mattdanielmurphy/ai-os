---
id: "auto-git-commits"
status: "todo"
priority: "medium"
assignee: null
epic: null
dueDate: null
created: "2026-07-08T01:22:03.696Z"
modified: "2026-07-08T01:22:03.696Z"
completedAt: null
labels: []
order: "a17"
---
# Automated Git Commits

For git commits in particular, it should just finish, and when it finishes, we commit everything with a dead simple script that just heavily summarizes what the agent said its task was. In fact, we could ask the agent to provide what it would say as a git commit message, and then our script just commits automatically. This accomplishes two things: a tiny amount of token savings for the big model, and the user will see the response faster instead of having to wait for the git commit each time.
