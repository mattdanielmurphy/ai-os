# Agent Log: Clinical Trial Scraper & AI Evaluator Pipeline

**Date:** 2026-07-23 16:26

## Goal
Build a modular background service in `ai-os` (`services/clinical-trials/`) that scrapes ClinicalTrials.gov REST API v2 studies near Edmonton, AB, evaluates candidate eligibility against `context/clinical-profile.md` using an AI agent (Jules), writes structured personal notes to Obsidian under `Financial/Clinical Trials/`, triggers Hermes iMessage notifications, and schedules monthly clinical profile check-ins.

## User Feedback & Decisions
- Destination folder for notes changed to `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/Financial/Clinical Trials/` (treating trials as financial/income opportunities).
- Ineligible trials are ignored completely; only `MATCH` and `UNCERTAIN` trials generate Obsidian notes and Hermes alerts.
- Geographic search scope restricted to a 50-mile radius around Edmonton, AB.

## Changes Made
- Created `context/clinical-profile.md`: Baseline physical metrics (28yo, 6'1"-6'2", ~265 lbs, BMI ~34.5), medications (Mounjaro 7.5mg/wk, Prozac 20mg/day, Vitamin D), lifestyle habits (daily cannabis, sedentary), and location bounds.
- Created `services/clinical-trials/`:
  - `package.json`, `tsconfig.json`, `src/types.ts`: Service structure and TypeScript interfaces.
  - `src/fetcher.ts`: Bun TypeScript script querying ClinicalTrials.gov REST API v2 (`https://clinicaltrials.gov/api/v2/studies`) within 50mi of Edmonton for recruiting/not yet recruiting studies with age hard-filtering.
  - `src/evaluator.ts`: Rule & AI evaluation logic checking GLP-1/Mounjaro, cannabis, SSRI, physical activity, and BMI thresholds.
  - `src/notifier.ts`: Obsidian note writer and Hermes/macOS notification bridge.
  - `src/monthly_checkin.sh` & `com.matt.clinical-profile-checkin.plist`: Monthly check-in script and LaunchAgent template.
- Created `.github/workflows/clinical-trial-scraper.yml`: Scheduled weekly workflow with Jules AI invocation.
- Updated `.devtool/features/clinical-trial-scraper.md`: Moved status to `review`.

## What Worked
- `bun run src/fetcher.ts` fetched 100 raw studies and filtered 78 candidates fitting Edmonton location and 28yo age window.
- `bun run src/evaluator.ts` evaluated 78 candidates (73 qualified, 5 ineligible).
- `bun run src/notifier.ts` wrote 73 structured Markdown notes to Obsidian under `Financial/Clinical Trials/` and triggered desktop alerts.

## What Didn't Work / Known Issues
- None. All components executed cleanly with Bun and standard APIs.

## Architecture Notes
- Future background tasks and Jules-driven jobs in `ai-os` can follow this exact pattern under `services/<job-name>/` with standard `bun run fetch`, `bun run eval`, `bun run notify` entrypoints.
