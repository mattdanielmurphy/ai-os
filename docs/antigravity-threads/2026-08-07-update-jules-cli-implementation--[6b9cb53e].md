---
title: "Update Jules CLI Implementation"
date: "2026-08-07"
conversation_id: "6b9cb53e-c566-480b-812e-be19407018d6"
source: "antigravity"
---

# Update Jules CLI Implementation

## User

Please update /Users/matt/projects/jules-burner/src/daemon/jules_cli.ts:

1. Update `remoteNew(repo: string, promptFilePath: string)`:
Read `promptFilePath` file contents using `readFileSync(promptFilePath, 'utf-8')`.
Pass prompt content via `--session` argument to `jules remote new`:
`return this.runCommand(["remote", "new", "--repo", repo, "--session", promptContent]);`

2. Update `parseResult(exitCode: number, stdout: string, stderr: string)`:
Extract numeric session ID from `stdout` or `stderr` when `ID: <number>` is matched:
```ts
const realIdMatch = stdout.match(/ID:\s*(\d+)/i) || stderr.match(/ID:\s*(\d+)/i);
if (realIdMatch) {
  sessionId = realIdMatch[1];
}
```
If `realIdMatch` is found, set `sessionId = realIdMatch[1]`.

3. Keep `runCommand` environment variables so PATH includes `${process.env.HOME}/.bun/bin`.

Ensure imports include `readFileSync` from `'fs'`.

---

## Assistant

Created At: 2026-08-06T19:54:27-06:00
Completed At: 2026-08-06T19:54:27-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/daemon/jules_cli.ts`
Total Lines: 157
Total Bytes: 4965
Showing lines 1 to 157
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { config } from "../config";
2: 
3: export interface JulesCommandResult {
4:   success: boolean;
5:   exitCode: number;
6:   stdout: string;
7:   stderr: string;
8:   sessionId?: string;
9:   status?: string;
10: }
11: 
12: export interface JulesSessionSummary {
13:   id: string;
14:   description: string;
15:   repo: string;
16:   lastActive: string;
17:   status: "Completed" | "Paused" | "In Progress" | string;
18: }
19: 
20: export type JulesExecutor = (args: string[]) => Promise<{ exitCode: number; stdout: string; stderr: string }>;
21: 
22: export interface JulesCLIOptions {
23:   cliPath?: string;
24:   executor?: JulesExecutor;
25:   timeoutMs?: number;
26: }
27: 
28: export class JulesCLI {
29:   private cliPath: string;
30:   private executor?: JulesExecutor;
31:   private timeoutMs: number;
32: 
33:   constructor(options: JulesCLIOptions = {}) {
34:     this.cliPath = options.cliPath ?? config.JULES_CLI_PATH;
35:     this.executor = options.executor;
36:     this.timeoutMs = options.timeoutMs ?? 30000;
37:   }
38: 
39:   private async runCommand(args: string[]): Promise<JulesCommandResult> {
40:     if (this.executor) {
41:       const res = await this.executor(args);
42:       return this.parseResult(res.exitCode, res.stdout, res.stderr);
43:     }
44: 
45:     try {
46:       const proc = Bun.spawn([this.cliPath, ...args], {
47:         stdout: "pipe",
48:         stderr: "pipe",
49:         env: { ...process.env, PATH: `${process.env.HOME}/.bun/bin:${process.env.PATH}` },
50:       });
51: 
52:       const timeoutPromise = new Promise<{ exitCo
<truncated 2085 bytes>
    const res = await this.runCommand(["remote", "new", "--repo", repo, "--prompt", promptFilePath]);
111:     if (!res.success) {
112:       console.error(`[jules_cli] remoteNew failed: ${res.stderr}`);
113:       console.error(`[jules_cli] stdout: ${res.stdout}`);
114:     } else {
115:       console.log(`[jules_cli] remoteNew output: ${res.stdout}`);
116:     }
117:     return res;
118:   }
119: 
120:   public async getStatus(sessionId: string): Promise<JulesCommandResult> {
121:     return this.runCommand(["status", "--session", sessionId]);
122:   }
123: 
124:   public async sync(sessionId: string): Promise<JulesCommandResult> {
125:     return this.runCommand(["sync", "--session", sessionId]);
126:   }
127: 
128:   public async listSessions(): Promise<{ success: boolean; sessions: JulesSessionSummary[]; raw: string }> {
129:     const res = await this.runCommand(["remote", "list", "--session"]);
130:     const sessions: JulesSessionSummary[] = [];
131:     if (res.success) {
132:       const lines = res.stdout.split("\n");
133:       for (const line of lines) {
134:         const parts = line.trim().split(/\s{2,}/);
135:         if (parts.length >= 4 && parts[0] !== "ID" && !parts[0].startsWith("ID")) {
136:           sessions.push({
137:             id: parts[0],
138:             description: parts[1] || "",
139:             repo: parts[2] || "mattdanielmurphy/jules-burner",
140:             lastActive: parts.length >= 5 ? parts[3] : "",
141:             status: parts[parts.length - 1] || "",
142:           });
143:         }
144:       }
145:     }
146:     return { success: res.success, sessions, raw: res.stdout };
147:   }
148: 
149:   public async pullSession(sessionId: string, apply: boolean = false): Promise<JulesCommandResult> {
150:     const args = ["remote", "pull", "--session", sessionId];
151:     if (apply) {
152:       args.push("--apply");
153:     }
154:     return this.runCommand(args);
155:   }
156: }
157: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-06T19:54:30-06:00
Completed At: 2026-08-06T19:54:30-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/jules-burner/src/daemon/jules_cli.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -1,4 +1,5 @@
 import { config } from "../config";
+import { readFileSync } from 'fs';
 
 export interface JulesCommandResult {
   success: boolean;
@@ -89,6 +89,11 @@
       }
     }
 
+    const realIdMatch = stdout.match(/ID:\s*(\d+)/i) || stderr.match(/ID:\s*(\d+)/i);
+    if (realIdMatch) {
+      sessionId = realIdMatch[1];
+    }
+
     let status: string | undefined;
     const statusMatch = stdout.match(/status:\s*([a-zA-Z_]+)/i);
     if (statusMatch) {
@@ -105,7 +105,8 @@
   }
 
   public async remoteNew(repo: string, promptFilePath: string): Promise<JulesCommandResult> {
-    const res = await this.runCommand(["remote", "new", "--repo", repo, "--prompt", promptFilePath]);
+    const promptContent = readFileSync(promptFilePath, 'utf-8');
+    const res = await this.runCommand(["remote", "new", "--repo", repo, "--session", promptContent]);
     if (!res.success) {
       console.error(`[jules_cli] remoteNew failed: ${res.stderr}`);
       console.error(`[jules_cli] stdout: ${res.stdout}`);
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-06T19:54:31-06:00
Completed At: 2026-08-06T19:54:31-06:00
Message sent to "a50c7f96-5f08-4c4e-82e3-d475dc73889b".

The requested updates have been applied to `/Users/matt/projects/jules-burner/src/daemon/jules_cli.ts`:

1.  **Imports:** Added `readFileSync` from `'fs'`.
2.  **`remoteNew`:** Now reads the contents of the `promptFilePath` file and passes the content to the `jules remote new` command using the `--session` argument.
3.  **`parseResult`:** Now includes logic to extract numeric session IDs from the `stdout` or `stderr` when they match the `ID: <number>` pattern.
4.  **`runCommand`:** Environment variables and PATH modifications remain preserved.

The file has been successfully updated.

---
