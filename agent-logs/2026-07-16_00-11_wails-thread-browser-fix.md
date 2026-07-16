# Agent Log - 2026-07-16 Wails Thread Browser NULL Fix

## Goal
Fix the thread browser displaying only 9 threads due to database scan errors.
- Uncovered that `cwd` and `content` are nullable columns in `sessions` and `messages` tables.
- Since standard Go `rows.Scan` fails when encountering a NULL value scanned into a string, most rows were silently skipped.

## User Feedback & Decisions
- User reported that the app only found 9 threads when there should be over 1000.

## Changes Made
- Wrapped nullable columns in SQL queries with `COALESCE` in `app.go`:
  - `COALESCE(title, ')` 
  - `COALESCE(cwd, ')` 
  - `COALESCE(content, ')` 
- Added explicit log output on scan errors inside Go database loops to prevent silent failures.
- Fixed a brace nesting syntax error in `app.go`.

## What Worked
- SQLite queries now successfully scan all 1891 rows, regardless of NULL `cwd` values.
- Re-compilation of the application completed successfully.

## What Didn't Work / Known Issues
- None.