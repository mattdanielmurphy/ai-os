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
