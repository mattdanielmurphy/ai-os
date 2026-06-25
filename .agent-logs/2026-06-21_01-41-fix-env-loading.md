## Goal
Allow the AI-OS Gateway to be run from directories other than the codebase root directory without throwing a "Missing GEMINI_API_KEY" error.

## Changes Made
- Modified `src/index.js` to resolve the codebase installation root using `import.meta.url`.
- Created a `loadEnvFile` helper function to read `.env` files.
- Loaded `.env` first from the codebase root (`CODEBASE_ROOT`) to import global configurations like `GEMINI_API_KEY`, then from the current working directory (`PROJECT_ROOT`) to allow local overrides.
- Updated `FEATURES.md` to document the new Multi-Directory Portability support.

## What Worked
- Verified via `node ../src/index.js --help` executed from the `./tmp` folder that the gateway successfully loaded `GEMINI_API_KEY` from the project root and completed the command without error.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The gateway distinguishes between `CODEBASE_ROOT` (where the gateway codebase resides, used for global assets/config like the `.env` API keys) and `PROJECT_ROOT` (defined by `process.cwd()`, representing the targeted workspace where sandbox constraints and rulebooks are defined).
