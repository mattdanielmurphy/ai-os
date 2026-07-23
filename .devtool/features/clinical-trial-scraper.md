---
id: clinical-trial-scraper
status: review
priority: medium
assignee: null
epic: null
dueDate: null
created: 2026-07-23
modified: 2026-07-23
completedAt: null
labels: ["clinical-trials", "services", "jules", "hermes"]
order: 1
---

# Clinical Trial Scraper & AI Evaluator Pipeline

Design and implement a modular background service (`services/clinical-trials/`) in Bun/TypeScript that scrapes ClinicalTrials.gov REST API v2 studies near Edmonton, AB, evaluates candidate study eligibility against `context/clinical-profile.md` using Jules via GitHub Actions, writes detailed personal notes to Obsidian under `Financial/Clinical Trials/`, triggers iMessage notifications via Hermes for matches/uncertains, and sets up a monthly check-in schedule.
