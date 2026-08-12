---
title: Context Packing Strategy
description: Strategy and rationale for codebase packing (repomix) when generating context for planner models.
tags: [architecture, agents, context, repomix]
---

# Context Packing Strategy for AI Agents

When we initiate high-reasoning planning via the `/planner` slash command, we use `repomix` to bundle the entire codebase into a single markdown file (`context.md`). Because large codebases can easily exceed token limits (e.g., reaching tens of millions of tokens), we apply strict exclusions.

However, the way we handle exclusions is critical to ensuring the agent accurately understands the repository state.

## The Problem with Blanket Exclusions
If we were to completely ignore all non-source files (such as media, archives, and databases) via `repomix`'s `--ignore` glob flags, those files would entirely vanish from the generated directory tree. 

If an agent cannot see a `.zip`, `.png`, or `.sqlite` file in the repository tree, it might conclude that the file doesn't exist. This can lead to hallucinations ("I need to create this image asset because it's missing") or confusion ("Why is this feature failing when the database file isn't even in the project?").

## Our Solution: Selective Exclusion

To solve this, our packing strategy splits the handling of unwanted files into two categories: **Explicit Glob Ignores** and **Native Binary Detection**.

### 1. Explicit Glob Ignores (Fully Excluded)
We explicitly pass glob patterns to `repomix --ignore` for files and directories that the agent **does not need to know exist**. This keeps the directory tree clean and focused.

We fully ignore:
- **Version Control**: `.git`, `.svn`
- **Dependencies**: `node_modules`, `vendor`, `Pods`, `packages`
- **Build/Caches**: `build/`, `dist/`, `.next/`, `__pycache__`, `.cache/`
- **Secrets/Env**: `.env*`, `*.pem`, `*.key`, `secrets.json`, `credentials.json`
- **Lockfiles**: `*.lock`, `pnpm-lock.yaml`, `bun.lockb`
- **IDE/OS Metadata**: `.idea`, `.vscode`, `.DS_Store`
- **Logs/Coverage**: `coverage/`, `*.log`

### 2. Native Binary Detection (Tree-Only Inclusion)
For files that are important to the project structure but should not have their raw bytes injected into the context window, we **do not** include them in the explicit ignore list.

Instead, we rely on `repomix`'s native binary file detection. Repomix automatically detects binary files and omits their *contents*, but still renders their file paths in the generated directory structure and logs them under "Binary Files Detected".

We deliberately leave these out of the ignore globs:
- **Media**: `*.png`, `*.jpg`, `*.svg`, `*.mp4`, `*.mp3`
- **Archives**: `*.zip`, `*.tar.gz`, `*.rar`
- **Databases**: `*.sqlite`, `*.db`
- **Compiled Binaries**: `*.exe`, `*.dll`, `*.so`

### Summary
By carefully splitting these exclusions, the agent receives a complete, accurate map of the project's structure (including where images, zips, and databases live) without reading their raw bytes into context, while still strictly ignoring all the noisy junk, secrets, and lockfiles.
