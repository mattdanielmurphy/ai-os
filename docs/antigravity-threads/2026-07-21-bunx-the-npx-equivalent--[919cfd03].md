---
title: "Bunx: The npx Equivalent"
date: "2026-07-21"
conversation_id: "919cfd03782999c3"
source: "antigravity"
---

# Bunx: The npx Equivalent

## User

is there a way to do npx with bun? bunx isn't it?

---

## Assistant

Yes, **`bunx`** (or **`bun x`**) **is** the direct equivalent of `npx`.

Both commands let you execute a package on the fly without installing it globally or adding it to your `package.json`.

Bash

```
# These two commands do the exact same thing:
bunx create-react-app my-app
bun x create-react-app my-app

```

How `bunx` Works Compared to `npx`

**Local first:** If the package binary exists in your project's `node_modules/.bin`, `bunx` executes that local version immediately.

**On-the-fly fetch:** If it's not installed locally, Bun fetches it from the npm registry, caches it globally in `~/.bun/install/cache`, and runs it.

**Speed:** Because of Bun's global package cache and fast startup, subsequent runs of `bunx` are virtually instant compared to `npx`.

Common Gotchas

If you ran into an issue using `bunx`, it's usually due to one of these subtle differences:

**Scoped packages:** For scoped packages, ensure you include the full scope:

Bash

```
bunx @storybook/cli init

```


**Package vs. Binary name differences:** Like `npx`, if a package's binary name differs from the package name, specify the executable or package flag if needed:

Bash

```
bunx --bun <package-name>

```


**Forcing Bun's runtime (`--bun`):** By default, if a package has a `#!/usr/bin/env node` shebang, Bun will run it using Node.js if Node is installed. If you want to force Bun to execute the package using Bun's own runtime for extra speed, pass the `--bun` flag:

Bash

```
bunx --bun prisma studio

```

---
