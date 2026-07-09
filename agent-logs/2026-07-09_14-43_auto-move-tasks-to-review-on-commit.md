## Goal
Automatically move any active features (`status: "in-progress"`) to the "Review" column (`status: "review"`) in the YAML frontmatter right before staging and committing.

## User Feedback & Decisions
Update `auto_commit.py` to intercept active features and change their status to `"review"`.

## Changes Made
- Modified [scripts/auto_commit.py](file:///Users/matt/projects/ai-os/scripts/auto_commit.py) to look for task files in `.devtool/features/*.md` containing `status: "in-progress"`.
- If found, it automatically rewrites the YAML frontmatter status to `"review"` before running `git add .`.

## What Worked
Running the updated script correctly captures and transitions active tasks to review status automatically, then stages the transition along with the rest of the workspace changes.

## What Didn't Work / Known Issues
None.

## Architecture Notes
This coordinates task closure and submission for review directly with the automatic git commit step.
