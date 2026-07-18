# Gemini Thread Categorization (On Hold)

## Overview
There is a file called `hermes_collection_manifest.json` that contains a nested mapping of Gemini conversation threads to specific `Categories` and `Collections`. 

We originally explored the idea of using this manifest to automatically sort the raw exported `.md` thread files into a hierarchy of subdirectories (e.g., `threads/Category/Collection/thread.md`) before they were ingested by Hermes. We even successfully injected `category` and `collection` tags into the YAML frontmatter.

## Why it's on hold
The idea was scrapped because of how the Hermes database and UI map "projects". In Hermes, projects are directly equivalent to these physical subdirectories (and are only designed to be one level deep). 

If we applied the categorization:
1. It would map every random Gemini chat topic into its own isolated Hermes project.
2. The user's main projects list would become incredibly bloated with dozens of generic categories (like "Lifestyle & Hobbies", "System Administration", etc.) that aren't actually useful day-to-day.
3. Threads need to be managed flexibly, and hard-mapping them to rigid project folders destroys the utility of the Hermes UI for actual active work.

## Potential Future Implementation
If we ever decide to revisit this:
- **Do not use folders:** Instead of moving the physical markdown files into directories, keep the `threads/` folder entirely flat.
- **Use YAML Frontmatter tags:** Inject the category metadata directly into the YAML frontmatter of the `.md` files (e.g. `category: "Technology"`).
- **Update the Database Schema:** Modify the Hermes sqlite database to natively support and index `categories` and `collections` as generic tags instead of mapping them to the rigid `project_id` concept. This would allow the Hermes UI to provide flexible tag-based filtering without destroying the projects list.
