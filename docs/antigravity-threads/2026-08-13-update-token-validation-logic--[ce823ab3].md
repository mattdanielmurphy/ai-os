---
title: "Update Token Validation Logic"
date: "2026-08-13"
conversation_id: "ce823ab3-7f59-4bac-82eb-4bf6088e5644"
source: "antigravity"
---

# Update Token Validation Logic

## User

In /Users/matt/projects/ai-os/services/perplexity-code-bridge/src/auth.ts, update validateRequestToken so that:
1. If process.env.DISABLE_TOKEN_AUTH === "true", return true (allowing header-free / query-free public access for testing).
2. Allow token to be checked via Authorization header (Bearer <token>).
3. Allow token to be passed via unguessable path prefix if configured.

Here is the exact replace for validateRequestToken in auth.ts:

export function validateRequestToken(req: Request, expectedToken: string): boolean {
  if (process.env.DISABLE_TOKEN_AUTH === "true") {
    return true;
  }

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

---

## Assistant

The requested changes to `validateRequestToken` in `/Users/matt/projects/ai-os/services/perplexity-code-bridge/src/auth.ts` have been implemented. The function now supports testing bypass via the `DISABLE_TOKEN_AUTH` environment variable, checking for the token in the `Authorization` header, and allowing the token to be passed as a path prefix.

---
