# Markdown-First Habit Tracking System

This document outlines the markdown-first, zero-database schema for tracking habits using Obsidian-style wikilinks and YAML frontmatter.

---

## 1. Directory Structure

All habit tracking documents reside in a structured directory inside the Obsidian vault or personal vault:

```text
habits/
├── definitions/
│   ├── Exercise.md
│   └── Read 30 Mins.md
└── logs/
    ├── 2026-07-17.md
    └── 2026-07-18.md
```

---

## 2. Habit Definition Schema

Each habit has a corresponding definition file in the `definitions/` directory. The filename is the exact habit name.

### Example: `habits/definitions/Read 30 Mins.md`

```markdown
---
type: habit
category: Mind
frequency: daily
target_days: 5  # target completions per week
created: 2026-07-01
---
# Read 30 Mins

Read a non-fiction book for at least 30 minutes every day to expand vocabulary and knowledge.
```

---

## 3. Daily Log Schema

Each day has a log file in the `logs/` directory named `YYYY-MM-DD.md`.

### Example: `habits/logs/2026-07-18.md`

```markdown
---
type: daily-log
date: 2026-07-18
completed:
  - [[Read 30 Mins]]
  - [[Exercise]]
notes: "Felt very productive today. Finished chapter 3 of the Rust book."
---
# Daily Log: 2026-07-18

Worked on ai-os and did some workout in the evening.
```

---

## 4. Graph Construction & Visualization

By parsing the frontmatter in `logs/*.md`:
- Each `[[WikiLink]]` in the `completed` field creates a bi-directional edge: `Date` <-> `Habit`.
- A parser builds a zero-database knowledge graph of habits and completion timelines.
- The completion data is programmatically formatted into pure SVG strings (e.g., contribution heatmaps or punch-cards) for visual rendering without frontend dependencies.
