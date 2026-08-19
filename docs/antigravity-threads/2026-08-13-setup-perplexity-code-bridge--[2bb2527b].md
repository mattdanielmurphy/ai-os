---
title: "Setup Perplexity Code Bridge"
date: "2026-08-13"
conversation_id: "2bb2527b-e52c-4907-9352-c302970606d1"
source: "antigravity"
---

# Setup Perplexity Code Bridge

## User

Create directory and files:

Target File: /Users/matt/projects/ai-os/services/perplexity-code-bridge/package.json
Content:
{
  "name": "perplexity-code-bridge",
  "version": "1.0.0",
  "description": "Live Codebase Context Bridge for Perplexity",
  "main": "src/index.ts",
  "type": "module",
  "scripts": {
    "start": "bun run src/index.ts",
    "test": "bun test"
  },
  "dependencies": {
    "ignore": "^7.0.5"
  },
  "devDependencies": {
    "@types/bun": "latest"
  }
}

Target File: /Users/matt/projects/ai-os/services/perplexity-code-bridge/src/auth.ts
Content:
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { randomBytes } from "node:crypto";

const CONFIG_DIR = join(homedir(), ".config", "perplexity-code-bridge");
const TOKEN_FILE = join(CONFIG_DIR, "token.json");

export function getOrGenerateToken(): string {
  if (!existsSync(CONFIG_DIR)) {
    mkdirSync(CONFIG_DIR, { recursive: true });
  }

  if (existsSync(TOKEN_FILE)) {
    try {
      const data = JSON.parse(readFileSync(TOKEN_FILE, "utf-8"));
      if (data && typeof data.token === "string" && data.token.length > 0) {
        return data.token;
      }
    } catch {
      // Fall through to generate new token
    }
  }

  const newToken = randomBytes(24).toString("hex");
  writeFileSync(TOKEN_FILE, JSON.stringify({ token: newToken }, null, 2), { mode: 0o600 });
  return newToken;
}

export function validateRequestToken(req: Request, expectedToken: string): boolean {
  const url = new URL(req.url);
  const tokenParam = url.searchParams.get("token");
  if (tokenParam && tokenParam === expectedToken) {
    return true;
  }

  const authHeader = req.headers.get("Authorization");
  if (authHeader && authHeader.startsWith("Bearer ")) {
    const bearerToken = authHeader.slice(7).trim();
    if (bearerToken === expectedToken) {
      return true;
    }
  }

  return false;
}

Target File: /Users/matt/projects/ai-os/services/perplexity-co
<truncated 6440 bytes>
th, entry.name);
            if (filter.isIgnored(full)) return null;
            const rel = relative(absoluteRootDir, full);
            const isDir = entry.isDirectory();
            const size = isDir ? undefined : statSync(full).size;
            return { name: entry.name, isDir, path: `/${rel}`, size };
          })
          .filter((item): item is NonNullable<typeof item> => item !== null);

        const currentRelDir = relative(absoluteRootDir, targetPath) || "root";
        return new Response(renderDirectoryView(currentRelDir, items, expectedToken), { headers });
      } else {
        try {
          const content = readFileSync(targetPath, "utf-8");
          const relFile = relative(absoluteRootDir, targetPath);
          return new Response(renderFileView(relFile, content), { headers });
        } catch (err) {
          return new Response("Error reading file", { status: 500, headers: { "Content-Type": "text/plain" } });
        }
      }
    }
  };
}

Target File: /Users/matt/projects/ai-os/services/perplexity-code-bridge/src/index.ts
Content:
import { getOrGenerateToken, validateRequestToken } from "./auth.js";
import { createBridgeServer } from "./server.js";

const rootDir = process.env.BRIDGE_ROOT || process.cwd();
const port = parseInt(process.env.PORT || "10000", 10);
const token = getOrGenerateToken();

const handler = createBridgeServer(rootDir, token, validateRequestToken);

Bun.serve({
  port,
  fetch: handler.fetch
});

console.log(`\n==================================================`);
console.log(`🚀 Live Codebase Context Bridge for Perplexity running!`);
console.log(` Root Directory : ${rootDir}`);
console.log(` Local URL      : http://localhost:${port}/?token=${token}`);
console.log(` Manifest URL   : http://localhost:${port}/manifest?token=${token}`);
console.log(`\n Access Token   : ${token}`);
console.log(`==================================================\n`);

---

## Assistant

The directory and files for `perplexity-code-bridge` have been successfully created at `/Users/matt/projects/ai-os/services/perplexity-code-bridge/`.

---
