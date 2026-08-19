---
title: "Write the complete file `/Users/matt/projects/jules-burner/src/daemon/jules_cli.ts` using `write_to_file` (Overwrite: true)."
date: "2026-08-07"
conversation_id: "f79a683f-b491-42ca-b1ea-8d0e4fad4562"
source: "antigravity"
---

# Write the complete file `/Users/matt/projects/jules-burner/src/daemon/jules_cli.ts` using `write_to_file` (Overwrite: true).

## User

Write the complete file `/Users/matt/projects/jules-burner/src/daemon/jules_cli.ts` using `write_to_file` (Overwrite: true).

Do not truncate.

```ts
import { spawn } from "node:child_process";
import { config } from "../config";
import { readFileSync, existsSync } from "node:fs";

export interface JulesCommandResult {
  success: boolean;
  exitCode: number;
  stdout: string;
  stderr: string;
  sessionId?: string;
  status?: string;
}

export interface JulesSessionSummary {
  id: string;
  description: string;
  repo: string;
  lastActive: string;
  status: string;
}

export type JulesExecutor = (args: string[]) => Promise<{ exitCode: number; stdout: string; stderr: string }>;

export interface JulesCLIOptions {
  cliPath?: string;
  executor?: JulesExecutor;
}

export class JulesCLI {
  private cliPath: string;
  private customExecutor?: JulesExecutor;

  constructor(options: JulesCLIOptions = {}) {
    this.cliPath = options.cliPath ?? config.JULES_CLI_PATH;
    this.customExecutor = options.executor;
  }

  public async runCommand(args: string[]): Promise<JulesCommandResult> {
    if (this.customExecutor) {
      const result = await this.customExecutor(args);
      return this.parseResult(result.exitCode, result.stdout, result.stderr);
    }

    return new Promise((resolve) => {
      let stdout = "";
      let stderr = "";

      const child = spawn(this.cliPath, args, {
        env: {
          ...process.env,
          GH_TOKEN: config.GITHUB_TOKEN,
          PATH: process.env.PATH,
        },
      });

      child.stdout.on("data", (data) => {
        stdout += data.toString();
      });

      child.stderr.on("data", (data) => {
        stderr += data.toString();
      });

      child.on("close", (code) => {
        const exitCode = code ?? 0;
        resolve(this.parseResult(exitCode, stdout, stderr));
      });

      child.on("error", (err) => {
        resolve({
          success: false,
          exitCode: -1,
          stdout: "",
          stderr: err.message,
        });
      
<truncated 782 bytes>
JulesCommandResult> {
    let promptContent = promptFilePath;
    if (existsSync(promptFilePath)) {
      promptContent = readFileSync(promptFilePath, "utf-8");
    }
    const res = await this.runCommand(["remote", "new", "--repo", repo, "--session", promptContent]);
    if (!res.success) {
      console.error(`[jules_cli] remoteNew failed: ${res.stderr}`);
      console.error(`[jules_cli] stdout: ${res.stdout}`);
    } else {
      console.log(`[jules_cli] remoteNew output: ${res.stdout}`);
    }
    return res;
  }

  public async getStatus(sessionId: string): Promise<JulesCommandResult> {
    return this.runCommand(["status", "--session", sessionId]);
  }

  public async sync(sessionId: string): Promise<JulesCommandResult> {
    return this.runCommand(["sync", "--session", sessionId]);
  }

  public async listSessions(): Promise<{ success: boolean; sessions: JulesSessionSummary[]; raw: string; exitCode: number }> {
    const res = await this.runCommand(["remote", "list", "--session"]);
    const sessions: JulesSessionSummary[] = [];
    if (res.success) {
      const lines = res.stdout.split("\n");
      for (const line of lines) {
        const parts = line.trim().split(/\s{2,}/);
        if (parts.length >= 4 && parts[0] !== "ID" && !parts[0].startsWith("ID")) {
          sessions.push({
            id: parts[0],
            description: parts[1] || "",
            repo: parts[2] || "mattdanielmurphy/jules-burner",
            lastActive: parts.length >= 5 ? parts[3] : "",
            status: parts[parts.length - 1] || "",
          });
        }
      }
    }
    return { success: res.success, sessions, raw: res.stdout, exitCode: res.exitCode };
  }

  public async pullSession(sessionId: string, apply = false): Promise<JulesCommandResult> {
    const args = ["remote", "pull", "--session", sessionId];
    if (apply) {
      args.push("--apply");
    }
    return this.runCommand(args);
  }
}
```

---
